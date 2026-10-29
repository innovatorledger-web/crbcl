"""Authentication API routes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import json
import logging

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
    PinStatusResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    ResendOtpRequest,
    ResetPasswordRequest,
    SetPinRequest,
    UpdateProfileRequest,
    UserInfo,
    VerifyOtpRequest,
    VerifyOtpResponse,
    VerifyPinRequest,
)
from app.auth.security import (
    create_reset_token,
    decode_reset_token,
    generate_csrf_token,
    get_cookie_settings,
    hash_password,
    verify_password,
)
from app.auth.service import AuthService
from app.core.config import get_settings
from app.core.database import get_db
from app.models.notification import Notification
from app.models.role import Role, UserRole
from app.models.user import User, UserPreference
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _set_auth_cookies(response: Response, access_token: str, refresh_token: str, csrf_token: str | None = None) -> None:
    """Set HttpOnly auth cookies and readable CSRF cookie for web clients."""
    settings = get_settings()
    cookie = get_cookie_settings(is_csrf=False)
    response.set_cookie(
        key="crbcl_access_token",
        value=access_token,
        max_age=settings.access_token_ttl,
        **cookie,
    )
    response.set_cookie(
        key="crbcl_refresh_token",
        value=refresh_token,
        max_age=settings.refresh_token_ttl,
        **cookie,
    )
    if csrf_token:
        csrf_cookie = get_cookie_settings(is_csrf=True)
        response.set_cookie(
            key="crbcl_csrf_token",
            value=csrf_token,
            max_age=settings.refresh_token_ttl,
            **csrf_cookie,
        )


def _clear_auth_cookies(response: Response) -> None:
    cookie = get_cookie_settings(is_csrf=False)
    csrf_cookie = get_cookie_settings(is_csrf=True)
    response.delete_cookie(key="crbcl_access_token", **cookie)
    response.delete_cookie(key="crbcl_refresh_token", **cookie)
    response.delete_cookie(key="crbcl_csrf_token", **csrf_cookie)


def _build_user_info(user: User, prefs: list[UserPreference] | None = None) -> UserInfo:
    roles = [ur.role.key for ur in user.roles if ur.role and ur.role.is_active]
    permissions = set()
    for ur in user.roles:
        if ur.role and ur.role.is_active:
            for rp in ur.role.permissions:
                if rp.permission and rp.permission.is_active:
                    permissions.add(rp.permission.key)

    # Use explicit prefs if provided, otherwise fallback to user.preferences
    prefs_list = prefs if prefs is not None else (user.preferences if hasattr(user, "preferences") else [])

    # Check preferences for persisted team_access
    team_access = []
    if prefs_list:
        pref = next((p for p in prefs_list if p.key == "team_access"), None)
        if pref and pref.value:
            try:
                loaded = json.loads(pref.value)
                if isinstance(loaded, list):
                    team_access = [str(x) for x in loaded]
            except Exception:
                team_access = []

    # Check preferences for avatar_url
    avatar_url = None
    if prefs_list:
        avatar_pref = next((p for p in prefs_list if p.key == "avatar_url"), None)
        if avatar_pref and avatar_pref.value:
            avatar_url = avatar_pref.value

    is_admin_or_leadership = (
        user.email == "admin@crbcl.ca"
        or "admin" in (user.email or "").lower()
        or getattr(user, "is_system", False)
        or "admin.users.manage" in permissions
        or any(r in roles for r in ["executive_director", "it_admin", "director_manager", "admin", "ceo"])
    )

    if user.email == "admin@crbcl.ca" or getattr(user, "is_system", False):
        for sys_role in ["it_admin", "executive_director", "ceo"]:
            if sys_role not in roles:
                roles.append(sys_role)

    if is_admin_or_leadership and (not team_access or "all" not in [str(t).lower() for t in team_access]):
        team_access = ["all"]

    is_super_admin = (
        user.email == "admin@crbcl.ca"
        or getattr(user, "is_system", False)
        or any(r in roles for r in ["admin", "system_admin", "administrator", "super_admin", "system administrator"])
    )
    if is_super_admin:
        from app.permissions.constants import Permissions

        permissions.update(p.value for p in Permissions)
    else:
        from app.core.seed import PERMISSIONS_DATA, ROLE_PERMISSIONS_MAP

        if any(r in roles for r in ["ceo", "executive_director", "chief_executive_officer"]):
            permissions.update(p["key"].value if hasattr(p["key"], "value") else str(p["key"]) for p in PERMISSIONS_DATA)
        else:
            for r in roles:
                for p in ROLE_PERMISSIONS_MAP.get(r, []):
                    permissions.add(p.value if hasattr(p, "value") else str(p))

    # Check preferences for appearance and widgets
    preferences = {}
    if prefs_list:
        for p in prefs_list:
            if p.key in ("appearance", "dashboard_widgets"):
                try:
                    preferences[p.key] = json.loads(p.value)
                except Exception:
                    preferences[p.key] = p.value

    return UserInfo(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        display_name=user.display_name,
        phone=user.phone,
        avatar_url=avatar_url,
        is_active=user.is_active,
        roles=roles,
        permissions=sorted(permissions),
        team_access=team_access,
        preferences=preferences,
        created_at=user.created_at,
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    response: Response,
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    auth = AuthService(db)
    user = await auth.authenticate(body.email, body.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Invalid email or password"}},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "USER_INACTIVE", "message": "Account is disabled"}},
        )

    access_token, refresh_token = await auth.create_session(
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, refresh_token, csrf_token)

    pref_res = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = pref_res.scalars().all()

    settings = get_settings()
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_ttl,
        user=_build_user_info(user, prefs=prefs),
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh(
    response: Response,
    body: RefreshRequest | None = None,
    db: AsyncSession = Depends(get_db),
    crbcl_refresh_token: str | None = Cookie(default=None),
):
    token_to_check = (body.refresh_token if body and body.refresh_token else None) or crbcl_refresh_token
    if not token_to_check:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "NO_REFRESH_TOKEN", "message": "No refresh token provided"}},
        )

    auth = AuthService(db)
    result = await auth.refresh_session(token_to_check)
    if not result:
        _clear_auth_cookies(response)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_REFRESH_TOKEN", "message": "Invalid or expired refresh token"}},
        )

    access_token, new_refresh_token = result
    await db.commit()

    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, new_refresh_token, csrf_token)

    settings = get_settings()
    return RefreshResponse(
        access_token=access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_ttl,
    )


@router.post("/logout", response_model=MessageResponse)
async def logout(
    response: Response,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    crbcl_refresh_token: str | None = Cookie(default=None),
):
    if crbcl_refresh_token:
        auth = AuthService(db)
        await auth.revoke_session(crbcl_refresh_token)
        await db.commit()
    _clear_auth_cookies(response)
    return MessageResponse(message="Logged out successfully")


@router.get("/me", response_model=UserInfo)
async def me(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    pref_res = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = pref_res.scalars().all()
    return _build_user_info(user, prefs=prefs)


@router.patch("/me", response_model=UserInfo)
async def update_profile(
    body: UpdateProfileRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.full_name is not None:
        user.full_name = body.full_name.strip()
    if body.display_name is not None:
        user.display_name = body.display_name.strip() or None
    if body.phone is not None:
        user.phone = body.phone.strip() or None

    if body.avatar_url is not None:
        pref_res = await db.execute(
            select(UserPreference).where(
                UserPreference.user_id == user.id,
                UserPreference.key == "avatar_url",
            )
        )
        pref = pref_res.scalars().first()
        if pref:
            pref.value = body.avatar_url
        else:
            pref = UserPreference(user_id=user.id, key="avatar_url", value=body.avatar_url)
            db.add(pref)

    await db.commit()
    auth = AuthService(db)
    fresh_user = await auth.get_user_by_id(user.id)
    pref_res = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = pref_res.scalars().all()
    return _build_user_info(fresh_user or user, prefs=prefs)


@router.post("/avatar")
async def upload_avatar(
    request: Request,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload or update user profile avatar for web and mobile platforms."""
    content_type = request.headers.get("content-type", "")
    avatar_val = None

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if uploaded_file and hasattr(uploaded_file, "read"):
            data = await uploaded_file.read()
            import base64
            b64_str = base64.b64encode(data).decode("utf-8")
            mime = getattr(uploaded_file, "content_type", "image/jpeg") or "image/jpeg"
            avatar_val = f"data:{mime};base64,{b64_str}"
    else:
        try:
            body = await request.json()
            avatar_val = body.get("avatar_url") or body.get("avatarUrl")
        except Exception:
            avatar_val = None

    if avatar_val is not None:
        pref_res = await db.execute(
            select(UserPreference).where(
                UserPreference.user_id == user.id,
                UserPreference.key == "avatar_url",
            )
        )
        pref = pref_res.scalars().first()
        if pref:
            pref.value = avatar_val
        else:
            pref = UserPreference(user_id=user.id, key="avatar_url", value=avatar_val)
            db.add(pref)
        await db.commit()

    return {"avatar_url": avatar_val, "success": True, "message": "Avatar updated successfully"}


@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    body: ChangePasswordRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your current password is incorrect. Please verify and try again.",
        )

    user.password_hash = hash_password(body.new_password)
    user.failed_login_count = 0
    user.locked_until = None
    await db.commit()

    return MessageResponse(
        success=True,
        message="Your password has been changed successfully.",
    )


VALID_PLATFORM_ROLES: frozenset[str] = frozenset({
    "it_admin",
    "executive_director",
    "ceo",
})


@router.post("/register", response_model=RegisterResponse)
async def register(body: RegisterRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    existing = await auth.get_user_by_email(body.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "EMAIL_EXISTS", "message": "An account with this email already exists"}},
        )

    requested_role = (body.requested_role or "caseworker").strip().lower()
    if requested_role not in VALID_PLATFORM_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_ROLE", "message": f"Requested role '{requested_role}' is not a valid platform role"}},
        )

    role_check = await db.execute(select(Role).where(Role.key == requested_role, Role.is_active.is_(True)))
    if not role_check.scalar_one_or_none():
        total_roles_count = (await db.execute(select(func.count(Role.id)))).scalar_one()
        if total_roles_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": {"code": "INVALID_ROLE", "message": f"Requested role '{requested_role}' is not active or recognized"}},
            )

    full_name = body.full_name or f"{body.first_name} {body.last_name}".strip()
    user = await auth.register_user(
        body.email,
        body.password,
        full_name=full_name,
        requested_role=requested_role,
        department=body.department or None,
    )

    # Queue administrative approval notification to Executive Directors & IT Admins
    try:
        admin_query = (
            select(User.id)
            .join(UserRole, UserRole.user_id == User.id)
            .join(Role, Role.id == UserRole.role_id)
            .where(Role.key.in_(["executive_director", "it_admin", "director_manager"]), User.is_active.is_(True))
        )
        admin_res = await db.execute(admin_query)
        admin_ids = set(admin_res.scalars().all())

        dept_label = f" ({body.department})" if body.department else ""
        role_label = requested_role.replace("_", " ").title()
        for admin_id in admin_ids:
            notif = Notification(
                recipient_id=admin_id,
                type="STAFF_REGISTRATION_REQUEST",
                title="New Staff Sign-Up Request",
                message=f"{full_name or body.email}{dept_label} has requested the '{role_label}' role and is awaiting administrative approval.",
                priority="HIGH",
                related_entity_type="user",
                related_entity_id=user.id,
            )
            db.add(notif)
    except Exception as e:
        logger.warning(f"Could not queue admin notification: {e}")

    # Generate and dispatch 6-digit verification code
    email_service = EmailService(db)
    await email_service.create_and_send_verification_code(body.email)

    await db.commit()
    return RegisterResponse(user_id=user.id, email=body.email)


@router.post("/verify-otp", response_model=VerifyOtpResponse)
async def verify_otp(
    request: Request,
    response: Response,
    body: VerifyOtpRequest,
    db: AsyncSession = Depends(get_db),
):
    email_service = EmailService(db)
    is_valid = await email_service.verify_otp(body.email, body.otp_code)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": {"code": "INVALID_OTP", "message": "Invalid or expired verification code"}},
        )

    auth = AuthService(db)
    user = await auth.get_user_by_email(body.email)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "User account not found or disabled"}},
        )

    access_token, refresh_token = await auth.create_session(
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    # OTP verification is a genuine login — delegate bookkeeping to the
    # single authoritative service method so all login paths are consistent.
    await auth.record_successful_login(user)
    await auth.db.flush()
    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, refresh_token, csrf_token)
    await db.commit()

    # Refresh user with roles/permissions loaded
    user = await auth.get_user_by_id(user.id)
    pref_res = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = pref_res.scalars().all()

    settings = get_settings()
    return VerifyOtpResponse(
        access_token=access_token,
        expires_in=settings.access_token_ttl,
        user=_build_user_info(user, prefs=prefs),
    )


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_otp(body: ResendOtpRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    user = await auth.get_user_by_email(body.email)
    if not user:
        return MessageResponse(message="If the account exists, a new verification code has been dispatched.")

    email_service = EmailService(db)
    await email_service.create_and_send_verification_code(body.email)
    await db.commit()
    return MessageResponse(message="Verification code sent to your email address")


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(body: ForgotPasswordRequest, db: AsyncSession = Depends(get_db)):
    auth = AuthService(db)
    user = await auth.get_user_by_email(body.email)
    if user and user.is_active and not user.is_deleted:
        reset_token = create_reset_token(user.id)
        email_service = EmailService(db)
        await email_service.send_password_reset_email(
            to_email=user.email,
            full_name=user.full_name or user.display_name or "Team Member",
            reset_token=reset_token,
        )
    return MessageResponse(
        message="If an account exists with that email, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(body: ResetPasswordRequest, db: AsyncSession = Depends(get_db)):
    if not body.reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token is required",
        )

    user_id = decode_reset_token(body.reset_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or has expired. Please request a new one.",
        )

    auth = AuthService(db)
    user = await auth.get_user_by_id(user_id)
    if not user or not user.is_active or user.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account not found or is currently inactive",
        )

    # Update password and reset lockout counters
    user.password_hash = hash_password(body.new_password)
    user.failed_login_count = 0
    user.locked_until = None

    # Revoke any active sessions for security
    await auth.revoke_all_user_sessions(user.id)
    await db.commit()

    return MessageResponse(
        message="Your password has been successfully reset. You can now log in with your new password."
    )


@router.post("/pin/set", response_model=MessageResponse)
async def set_pin(
    body: SetPinRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Set or update user's quick-access 6-digit PIN."""
    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == current_user.id,
            UserPreference.key == "quick_pin_hash",
        )
    )
    pref = result.scalars().first()
    hashed_pin = hash_password(body.pin)

    if pref:
        pref.value = hashed_pin
    else:
        pref = UserPreference(
            user_id=current_user.id,
            key="quick_pin_hash",
            value=hashed_pin,
        )
        db.add(pref)

    await db.commit()
    return MessageResponse(message="6-digit PIN saved successfully")


@router.post("/pin/verify", response_model=LoginResponse)
async def verify_pin(
    request: Request,
    response: Response,
    body: VerifyPinRequest,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate and create session via 6-digit PIN."""
    auth = AuthService(db)
    user = await auth.get_user_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_PIN", "message": "Invalid email or PIN"}},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "USER_INACTIVE", "message": "Account is disabled"}},
        )

    now = datetime.now(UTC)

    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == user.id,
            UserPreference.key == "quick_pin_hash",
        )
    )
    pref = result.scalars().first()

    pin_valid = bool(pref and pref.value and verify_password(body.pin, pref.value))

    if not pin_valid:
        if user.locked_until and user.locked_until > now:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"error": {"code": "ACCOUNT_LOCKED", "message": "Account is temporarily locked. Please try again later."}},
            )
        user.failed_login_count += 1
        if user.failed_login_count >= 5:
            user.locked_until = now + timedelta(minutes=15)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_PIN", "message": "Incorrect 6-digit PIN"}},
        )

    user.failed_login_count = 0
    user.locked_until = None
    user.last_login_at = now

    access_token, refresh_token = await auth.create_session(
        user,
        user_agent=request.headers.get("user-agent"),
        ip_address=request.client.host if request.client else None,
    )
    await db.commit()

    csrf_token = generate_csrf_token()
    _set_auth_cookies(response, access_token, refresh_token, csrf_token)

    pref_res = await db.execute(select(UserPreference).where(UserPreference.user_id == user.id))
    prefs = pref_res.scalars().all()

    settings = get_settings()
    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_ttl,
        user=_build_user_info(user, prefs=prefs),
    )


@router.get("/pin/status", response_model=PinStatusResponse)
async def check_pin_status(
    email: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Check whether a user has a 6-digit PIN configured on the backend."""
    auth = AuthService(db)
    user = await auth.get_user_by_email(email)
    if not user:
        return PinStatusResponse(has_pin=False, email=email)

    result = await db.execute(
        select(UserPreference).where(
            UserPreference.user_id == user.id,
            UserPreference.key == "quick_pin_hash",
        )
    )
    pref = result.scalars().first()
    return PinStatusResponse(has_pin=bool(pref and pref.value), email=email)


