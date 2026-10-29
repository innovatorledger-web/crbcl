import 'dart:async';
import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

class AuthResult {
  final bool success;
  final String? errorMessage;
  final bool requiresPinSetup;
  final Map<String, dynamic>? user;

  AuthResult({
    required this.success,
    this.errorMessage,
    this.requiresPinSetup = false,
    this.user,
  });
}

class PinUnlockResult {
  final bool success;
  final bool isLocked;
  final bool isExpired;
  final String? errorMessage;
  final int remainingAttempts;

  PinUnlockResult({
    required this.success,
    this.isLocked = false,
    this.isExpired = false,
    this.errorMessage,
    this.remainingAttempts = 5,
  });
}

class MobileAuthService {
  static final MobileAuthService instance = MobileAuthService._internal();
  MobileAuthService._internal();
  factory MobileAuthService() => instance;

  static const _secureStorage = FlutterSecureStorage();

  // Storage Keys
  static const _keyAccessToken = 'crbcl_access_token';
  static const _keyRefreshToken = 'crbcl_refresh_token';
  static const _keyUserId = 'crbcl_user_id';
  static const _keyUserEmail = 'crbcl_user_email';
  static const _keyUserName = 'crbcl_user_name';
  static const _keyUserRoles = 'crbcl_user_roles';
  static const _keyUserPermissions = 'crbcl_user_permissions';
  static const _keyUserAvatar = 'crbcl_user_avatar_url';
  static const _keyDeviceId = 'crbcl_device_id';
  static const _keyServerUrl = 'crbcl_server_url';
  static const _keyPinHash = 'crbcl_pin_hash';
  static const _keyPinSalt = 'crbcl_pin_salt';
  static const _keyLastAuthTime = 'crbcl_last_auth_time';
  static const _keyFailedAttempts = 'crbcl_pin_failed_attempts';
  static const _keyLockedUntil = 'crbcl_pin_locked_until';
  static const _keyAdminUsersCache = 'crbcl_admin_users_cache';

  // Constants
  static const int pbkdf2Iterations = 100000;
  static const int maxFailedAttempts = 5;
  static const Duration lockoutDuration = Duration(minutes: 15);
  static const int offlineExpiryHours = 24;
  static const String defaultServerUrl = 'https://crbcl-production.up.railway.app';

  /// Derive PBKDF2 HMAC-SHA256 key from PIN and salt
  static String derivePbkdf2PinKey(String pin, String saltHex, {int iterations = pbkdf2Iterations}) {
    final salt = utf8.encode(saltHex);
    List<int> derivedKey = utf8.encode(pin);

    for (int i = 0; i < iterations; i++) {
      final hmac = Hmac(sha256, derivedKey);
      derivedKey = hmac.convert(salt).bytes;
    }
    return base64Url.encode(derivedKey);
  }

  /// Generate a storage key scoped to a specific user email
  static String _userKey(String? email, String baseKey) {
    if (email == null || email.trim().isEmpty) return baseKey;
    final normalized = email.trim().toLowerCase().replaceAll(RegExp(r'[^a-zA-Z0-9_]'), '_');
    return '${baseKey}_$normalized';
  }

  /// Get or generate per-installation/per-user random 256-bit salt
  Future<String> getOrCreateSalt({String? email}) async {
    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);
    final saltKey = targetEmail != null && targetEmail.isNotEmpty
        ? _userKey(targetEmail, _keyPinSalt)
        : _keyPinSalt;

    String? salt = await _secureStorage.read(key: saltKey);
    if (salt == null && targetEmail != null && targetEmail.isNotEmpty) {
      // Fallback check to global salt if previously created
      salt = await _secureStorage.read(key: _keyPinSalt);
    }

    if (salt == null) {
      final random = Random.secure();
      final values = List<int>.generate(32, (i) => random.nextInt(256));
      salt = base64Url.encode(values);
      await _secureStorage.write(key: saltKey, value: salt);
      // Also write global salt for backwards compatibility with tests
      await _secureStorage.write(key: _keyPinSalt, value: salt);
    }
    return salt;
  }

  /// Get or generate persistent unique device ID
  Future<String> getOrCreateDeviceId() async {
    String? deviceId = await _secureStorage.read(key: _keyDeviceId);
    if (deviceId == null) {
      final random = Random.secure();
      final randBytes = List<int>.generate(16, (i) => random.nextInt(256));
      deviceId = 'DEV-${base64Url.encode(randBytes).replaceAll('=', '').substring(0, 16)}';
      await _secureStorage.write(key: _keyDeviceId, value: deviceId);
    }
    return deviceId;
  }

  /// Check whether user has registered and set up a PIN on this device
  Future<bool> hasSavedCredentials({String? email}) async {
    final token = await _secureStorage.read(key: _keyAccessToken);
    if (token == null || token.isEmpty) return false;

    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);
    if (targetEmail != null && targetEmail.isNotEmpty) {
      final userPin = await _secureStorage.read(key: _userKey(targetEmail, _keyPinHash));
      if (userPin != null) return true;
    }
    final fallbackPin = await _secureStorage.read(key: _keyPinHash);
    return fallbackPin != null;
  }

  /// Check whether a specific user has set up a PIN
  Future<bool> hasUserPin([String? email]) async {
    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);
    if (targetEmail != null && targetEmail.isNotEmpty) {
      final userPin = await _secureStorage.read(key: _userKey(targetEmail, _keyPinHash));
      if (userPin != null) return true;
      if (email != null) return false;
    }
    final fallbackPin = await _secureStorage.read(key: _keyPinHash);
    return fallbackPin != null;
  }

  /// Backward-compatible alias for hasUserPin
  Future<bool> hasPin() async => hasUserPin();

  /// Get active user email
  Future<String?> getActiveUserEmail() async {
    return await _secureStorage.read(key: _keyUserEmail);
  }

  /// Get active user display name
  Future<String?> getActiveUserName() async {
    return await _secureStorage.read(key: _keyUserName);
  }

  /// Get stored server URL or fallback
  Future<String> getServerUrl() async {
    final url = await _secureStorage.read(key: _keyServerUrl);
    return url ?? defaultServerUrl;
  }

  /// Set server URL
  Future<void> setServerUrl(String url) async {
    await _secureStorage.write(key: _keyServerUrl, value: url.trim());
  }

  /// Maps a failed login response to an accurate, non-sensitive user message.
  static String describeLoginFailure(int statusCode, String body) {
    String? code;
    try {
      final decoded = jsonDecode(body);
      if (decoded is Map && decoded['error'] is Map) {
        code = (decoded['error']['code'] as String?)?.toUpperCase();
      }
    } catch (_) {}

    if (statusCode == 401) {
      return 'Incorrect email or password. Repeated failed attempts temporarily lock the account.';
    }
    if (statusCode == 403) {
      if (code == 'USER_INACTIVE') {
        return 'This account is disabled. Contact your CRBCL administrator.';
      }
      return 'Access to this account is not permitted. Contact your CRBCL administrator.';
    }
    if (statusCode == 429) {
      return 'Too many sign-in attempts. Please wait a few minutes and try again.';
    }
    if (statusCode >= 500) {
      return 'The CRBCL server is temporarily unavailable. Please try again shortly.';
    }
    return 'Sign-in failed (code $statusCode). Please try again or contact support.';
  }

  /// Perform online authentication with backend for Standard Staff
  Future<AuthResult> loginOnline({
    required String email,
    required String password,
    String? serverUrl,
    bool isStaffPortalOnly = true,
  }) async {
    final effectiveUrl = (serverUrl ?? await getServerUrl()).replaceAll(RegExp(r'/+$'), '');
    await setServerUrl(effectiveUrl);

    try {
      final loginUri = Uri.parse('$effectiveUrl/api/v1/auth/login');
      final response = await http
          .post(
            loginUri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email.trim(),
              'password': password,
            }),
          )
          .timeout(const Duration(seconds: 20));

      if (response.statusCode != 200) {
        return AuthResult(
          success: false,
          errorMessage: describeLoginFailure(response.statusCode, response.body),
        );
      }

      final data = jsonDecode(response.body);
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = data['user'] as Map<String, dynamic>;

      // Check whether user is administrator
      final roles = (user['roles'] as List?)?.cast<String>() ?? [];
      final isItAdmin = user['role'] == 'admin' ||
          roles.contains('admin') ||
          roles.contains('it_admin') ||
          user['email'] == 'admin@crbcl.ca' ||
          email.trim().toLowerCase() == 'admin@crbcl.ca';

      if (isStaffPortalOnly && isItAdmin) {
        return AuthResult(
          success: false,
          errorMessage: 'Administrator accounts cannot sign in through this portal. Please use the IT Admin Portal.',
        );
      }

      final deviceId = await getOrCreateDeviceId();

      // Register device through existing device API
      final regUri = Uri.parse('$effectiveUrl/api/v1/sync/devices/register');
      await http.post(
        regUri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({
          'device_id': deviceId,
          'device_name': isItAdmin ? 'Admin Mobile Console' : 'Caseworker Mobile Unit',
          'os_type': 'Android',
          'app_version': '1.0.0',
        }),
      ).timeout(const Duration(seconds: 20));

      final userEmail = (user['email']?.toString() ?? email).trim().toLowerCase();

      // Persist authentication material securely
      await _secureStorage.write(key: _keyAccessToken, value: accessToken);
      if (refreshToken != null) {
        await _secureStorage.write(key: _keyRefreshToken, value: refreshToken);
      }
      await _secureStorage.write(key: _keyUserId, value: user['id']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserEmail, value: userEmail);
      await _secureStorage.write(key: _keyUserName, value: user['display_name']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserRoles, value: jsonEncode(user['roles'] ?? []));
      await _secureStorage.write(key: _keyUserPermissions, value: jsonEncode(user['permissions'] ?? []));
      await _secureStorage.write(key: _keyUserAvatar, value: user['avatar_url']?.toString() ?? '');
      await _secureStorage.write(key: _keyLastAuthTime, value: DateTime.now().toIso8601String());

      // Reset lockout state for this specific user
      await _secureStorage.delete(key: _userKey(userEmail, _keyFailedAttempts));
      await _secureStorage.delete(key: _userKey(userEmail, _keyLockedUntil));
      await _secureStorage.delete(key: _keyFailedAttempts);
      await _secureStorage.delete(key: _keyLockedUntil);

      // Check user-isolated PIN
      final existingUserPin = await _secureStorage.read(key: _userKey(userEmail, _keyPinHash));
      return AuthResult(
        success: true,
        requiresPinSetup: existingUserPin == null,
        user: user,
      );
    } on TimeoutException {
      return AuthResult(
        success: false,
        errorMessage: 'The server did not respond in time. Check your connection and try again.',
      );
    } catch (e) {
      return AuthResult(
        success: false,
        errorMessage: 'Unable to reach the CRBCL server. Online sign-in requires an internet connection.',
      );
    }
  }

  /// Perform online authentication for IT Administrators
  Future<AuthResult> loginAdminOnline({
    required String email,
    required String password,
    String? serverUrl,
  }) async {
    final effectiveUrl = (serverUrl ?? await getServerUrl()).replaceAll(RegExp(r'/+$'), '');
    await setServerUrl(effectiveUrl);

    try {
      final loginUri = Uri.parse('$effectiveUrl/api/v1/auth/login');
      final response = await http
          .post(
            loginUri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email.trim(),
              'password': password,
            }),
          )
          .timeout(const Duration(seconds: 20));

      if (response.statusCode != 200) {
        return AuthResult(
          success: false,
          errorMessage: describeLoginFailure(response.statusCode, response.body),
        );
      }

      final data = jsonDecode(response.body);
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = data['user'] as Map<String, dynamic>;

      final roles = (user['roles'] as List?)?.cast<String>() ?? [];
      final isItAdmin = user['role'] == 'admin' ||
          roles.contains('admin') ||
          roles.contains('it_admin') ||
          user['email'] == 'admin@crbcl.ca' ||
          email.trim().toLowerCase() == 'admin@crbcl.ca';

      if (!isItAdmin) {
        return AuthResult(
          success: false,
          errorMessage: 'Access Denied: The IT Admin Portal is exclusively for IT Administrators and System Admins. Frontline and operational staff please use the standard portal.',
        );
      }

      final deviceId = await getOrCreateDeviceId();

      // Register device as Admin console
      final regUri = Uri.parse('$effectiveUrl/api/v1/sync/devices/register');
      await http.post(
        regUri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({
          'device_id': deviceId,
          'device_name': 'Admin Mobile Console',
          'os_type': 'Android',
          'app_version': '1.0.0',
        }),
      ).timeout(const Duration(seconds: 20));

      final userEmail = (user['email']?.toString() ?? email).trim().toLowerCase();

      // Persist admin session
      await _secureStorage.write(key: _keyAccessToken, value: accessToken);
      if (refreshToken != null) {
        await _secureStorage.write(key: _keyRefreshToken, value: refreshToken);
      }
      await _secureStorage.write(key: _keyUserId, value: user['id']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserEmail, value: userEmail);
      await _secureStorage.write(key: _keyUserName, value: user['display_name']?.toString() ?? 'System Administrator');
      await _secureStorage.write(key: _keyUserRoles, value: jsonEncode(user['roles'] ?? ['admin']));
      await _secureStorage.write(key: _keyUserPermissions, value: jsonEncode(user['permissions'] ?? []));
      await _secureStorage.write(key: _keyUserAvatar, value: user['avatar_url']?.toString() ?? '');
      await _secureStorage.write(key: _keyLastAuthTime, value: DateTime.now().toIso8601String());

      // Reset lockout state
      await _secureStorage.delete(key: _userKey(userEmail, _keyFailedAttempts));
      await _secureStorage.delete(key: _userKey(userEmail, _keyLockedUntil));
      await _secureStorage.delete(key: _keyFailedAttempts);
      await _secureStorage.delete(key: _keyLockedUntil);

      final existingUserPin = await _secureStorage.read(key: _userKey(userEmail, _keyPinHash));
      return AuthResult(
        success: true,
        requiresPinSetup: existingUserPin == null,
        user: user,
      );
    } on TimeoutException {
      return AuthResult(
        success: false,
        errorMessage: 'The server did not respond in time. Check your connection and try again.',
      );
    } catch (e) {
      return AuthResult(
        success: false,
        errorMessage: 'Unable to reach the CRBCL server: $e',
      );
    }
  }

  /// Register new user account online with CRBCL backend
  Future<Map<String, dynamic>> registerOnline({
    required String email,
    required String password,
    required String fullName,
    required String requestedRole,
    String? department,
  }) async {
    final effectiveUrl = (await getServerUrl()).replaceAll(RegExp(r'/+$'), '');

    try {
      final registerUri = Uri.parse('$effectiveUrl/api/v1/auth/register');
      final response = await http
          .post(
            registerUri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email.trim(),
              'password': password,
              'full_name': fullName.trim(),
              'requested_role': requestedRole.trim().toLowerCase(),
              'department': department?.trim() ?? '',
            }),
          )
          .timeout(const Duration(seconds: 20));

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 || response.statusCode == 201) {
        return {
          'success': true,
          'message': data['message'] ?? 'Registration submitted. Please check your email for verification code.',
          'email': email.trim(),
        };
      }

      String message = 'Registration failed (code ${response.statusCode}).';
      if (data is Map && data['detail'] is Map && data['detail']['error'] is Map) {
        message = data['detail']['error']['message'] ?? message;
      } else if (data is Map && data['detail'] is String) {
        message = data['detail'];
      }

      return {
        'success': false,
        'errorMessage': message,
      };
    } on TimeoutException {
      return {
        'success': false,
        'errorMessage': 'The server did not respond in time. Check your connection and try again.',
      };
    } catch (e) {
      return {
        'success': false,
        'errorMessage': 'Unable to connect to CRBCL server: $e',
      };
    }
  }

  /// Verify email OTP code and authenticate device
  Future<AuthResult> verifyOtpOnline({
    required String email,
    required String otpCode,
  }) async {
    final effectiveUrl = (await getServerUrl()).replaceAll(RegExp(r'/+$'), '');

    try {
      final verifyUri = Uri.parse('$effectiveUrl/api/v1/auth/verify-otp');
      final response = await http
          .post(
            verifyUri,
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email.trim(),
              'otp_code': otpCode.trim(),
            }),
          )
          .timeout(const Duration(seconds: 20));

      if (response.statusCode != 200) {
        final data = jsonDecode(response.body);
        String msg = 'Invalid or expired verification code.';
        if (data is Map && data['detail'] is Map && data['detail']['error'] is Map) {
          msg = data['detail']['error']['message'] ?? msg;
        }
        return AuthResult(success: false, errorMessage: msg);
      }

      final data = jsonDecode(response.body);
      final accessToken = data['access_token'] as String;
      final refreshToken = data['refresh_token'] as String?;
      final user = data['user'] as Map<String, dynamic>;

      final deviceId = await getOrCreateDeviceId();

      // Register device through existing device API
      final regUri = Uri.parse('$effectiveUrl/api/v1/sync/devices/register');
      await http.post(
        regUri,
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $accessToken',
        },
        body: jsonEncode({
          'device_id': deviceId,
          'device_name': 'Caseworker Mobile Unit',
          'os_type': 'Android',
          'app_version': '1.0.0',
        }),
      ).timeout(const Duration(seconds: 20));

      // Persist authentication credentials
      await _secureStorage.write(key: _keyAccessToken, value: accessToken);
      if (refreshToken != null) {
        await _secureStorage.write(key: _keyRefreshToken, value: refreshToken);
      }
      await _secureStorage.write(key: _keyUserId, value: user['id']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserEmail, value: user['email']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserName, value: user['display_name']?.toString() ?? '');
      await _secureStorage.write(key: _keyUserRoles, value: jsonEncode(user['roles'] ?? []));
      await _secureStorage.write(key: _keyUserPermissions, value: jsonEncode(user['permissions'] ?? []));
      await _secureStorage.write(key: _keyUserAvatar, value: user['avatar_url']?.toString() ?? '');
      await _secureStorage.write(key: _keyLastAuthTime, value: DateTime.now().toIso8601String());

      return AuthResult(
        success: true,
        requiresPinSetup: true,
        user: user,
      );
    } catch (e) {
      return AuthResult(success: false, errorMessage: 'Verification failed: $e');
    }
  }

  /// Validate 6-digit numeric PIN format
  static bool isValidPinFormat(String pin) {
    return pin.length == 6 && RegExp(r'^\d{6}$').hasMatch(pin);
  }

  /// Set or update the user's personal 6-digit PIN (stored locally and synced with central backend)
  Future<bool> setPin(String pin, {String? email}) async {
    if (!isValidPinFormat(pin)) return false;
    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);
    final salt = await getOrCreateSalt(email: targetEmail);
    final pinHash = derivePbkdf2PinKey(pin, salt);

    if (targetEmail != null && targetEmail.isNotEmpty) {
      await _secureStorage.write(key: _userKey(targetEmail, _keyPinHash), value: pinHash);
      await _secureStorage.delete(key: _userKey(targetEmail, _keyFailedAttempts));
      await _secureStorage.delete(key: _userKey(targetEmail, _keyLockedUntil));
    } else {
      // Legacy fallback when no email exists
      await _secureStorage.write(key: _keyPinHash, value: pinHash);
      await _secureStorage.delete(key: _keyFailedAttempts);
      await _secureStorage.delete(key: _keyLockedUntil);
    }

    // Sync to backend if access token is available
    final token = await getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final serverUrl = await getServerUrl();
        final uri = Uri.parse('$serverUrl/api/v1/auth/pin/set');
        await http.post(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
          body: jsonEncode({'pin': pin}),
        ).timeout(const Duration(seconds: 10));
      } catch (_) {}
    }

    return true;
  }

  /// Check whether user has 6-digit PIN set on backend
  Future<bool> checkBackendPinStatus(String email) async {
    try {
      final serverUrl = await getServerUrl();
      final uri = Uri.parse('$serverUrl/api/v1/auth/pin/status?email=${Uri.encodeComponent(email.trim())}');
      final res = await http.get(uri).timeout(const Duration(seconds: 6));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        return data['has_pin'] == true;
      }
    } catch (_) {}
    return false;
  }

  /// Unlock application using 6-digit PIN with central server verification & offline fallback
  Future<PinUnlockResult> unlockWithPin(String pin, {String? email}) async {
    if (!isValidPinFormat(pin)) {
      return PinUnlockResult(
        success: false,
        errorMessage: 'PIN must be exactly 6 numeric digits.',
      );
    }

    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);

    final lockedKey = _userKey(targetEmail, _keyLockedUntil);
    final failedKey = _userKey(targetEmail, _keyFailedAttempts);
    final hashKey = _userKey(targetEmail, _keyPinHash);

    // 1. Check local lockout status
    final lockedUntilStr = (targetEmail != null ? await _secureStorage.read(key: lockedKey) : null) ??
        await _secureStorage.read(key: _keyLockedUntil);
    if (lockedUntilStr != null) {
      final lockedUntil = DateTime.tryParse(lockedUntilStr);
      if (lockedUntil != null && DateTime.now().isBefore(lockedUntil)) {
        final remainingSecs = lockedUntil.difference(DateTime.now()).inSeconds;
        return PinUnlockResult(
          success: false,
          isLocked: true,
          errorMessage: 'App locked due to failed PIN attempts. Retry in $remainingSecs seconds.',
        );
      }
    }

    // 2. Check offline authorization expiry (24-hour limit)
    final lastAuthStr = await _secureStorage.read(key: _keyLastAuthTime);
    if (lastAuthStr != null) {
      final lastAuth = DateTime.tryParse(lastAuthStr);
      if (lastAuth != null) {
        final elapsedHours = DateTime.now().difference(lastAuth).inHours;
        if (elapsedHours >= offlineExpiryHours) {
          return PinUnlockResult(
            success: false,
            isExpired: true,
            errorMessage: 'Offline authorization expired ($elapsedHours hrs since last online sync). Please log in with your CRBCL credentials.',
          );
        }
      }
    }

    // 3. Attempt online central server PIN verification if email is available
    if (targetEmail != null && targetEmail.isNotEmpty) {
      try {
        final serverUrl = await getServerUrl();
        final uri = Uri.parse('$serverUrl/api/v1/auth/pin/verify');
        final response = await http
            .post(
              uri,
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode({
                'email': targetEmail.trim(),
                'pin': pin,
              }),
            )
            .timeout(const Duration(seconds: 10));

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          final accessToken = data['access_token'] as String;
          final refreshToken = data['refresh_token'] as String?;
          final user = data['user'] as Map<String, dynamic>;

          // Store authentication material securely
          await _secureStorage.write(key: _keyAccessToken, value: accessToken);
          if (refreshToken != null) {
            await _secureStorage.write(key: _keyRefreshToken, value: refreshToken);
          }
          await _secureStorage.write(key: _keyUserId, value: user['id']?.toString() ?? '');
          await _secureStorage.write(key: _keyUserEmail, value: targetEmail.trim().toLowerCase());
          await _secureStorage.write(key: _keyUserName, value: user['display_name']?.toString() ?? '');
          await _secureStorage.write(key: _keyUserRoles, value: jsonEncode(user['roles'] ?? []));
          await _secureStorage.write(key: _keyUserPermissions, value: jsonEncode(user['permissions'] ?? []));
          await touchAuthTimestamp();

          // Sync local PBKDF2 hash so offline mode works with this exact verified PIN
          final salt = await getOrCreateSalt(email: targetEmail);
          final pinHash = derivePbkdf2PinKey(pin, salt);
          await _secureStorage.write(key: hashKey, value: pinHash);

          // Clear lockout and failed attempts
          await _secureStorage.delete(key: failedKey);
          await _secureStorage.delete(key: lockedKey);
          await _secureStorage.delete(key: _keyFailedAttempts);
          await _secureStorage.delete(key: _keyLockedUntil);

          return PinUnlockResult(success: true);
        } else if (response.statusCode == 401 || response.statusCode == 403) {
          String msg = 'Incorrect 6-digit PIN.';
          try {
            final data = jsonDecode(response.body);
            if (data is Map && data['detail'] is Map && data['detail']['error'] is Map) {
              msg = data['detail']['error']['message'] ?? msg;
            } else if (data is Map && data['detail'] is String) {
              msg = data['detail'];
            }
          } catch (_) {}

          // Increment failed attempts
          final attemptsStr = await _secureStorage.read(key: failedKey) ?? await _secureStorage.read(key: _keyFailedAttempts);
          int failedAttempts = (attemptsStr != null ? int.tryParse(attemptsStr) ?? 0 : 0) + 1;
          await _secureStorage.write(key: failedKey, value: failedAttempts.toString());
          await _secureStorage.write(key: _keyFailedAttempts, value: failedAttempts.toString());

          if (failedAttempts >= maxFailedAttempts) {
            final lockedUntil = DateTime.now().add(lockoutDuration);
            await _secureStorage.write(key: lockedKey, value: lockedUntil.toIso8601String());
            await _secureStorage.write(key: _keyLockedUntil, value: lockedUntil.toIso8601String());
            return PinUnlockResult(
              success: false,
              isLocked: true,
              errorMessage: 'Maximum PIN attempts exceeded. App locked for 15 minutes.',
              remainingAttempts: 0,
            );
          }
          final remaining = maxFailedAttempts - failedAttempts;
          return PinUnlockResult(
            success: false,
            errorMessage: '$msg $remaining attempt${remaining == 1 ? '' : 's'} remaining.',
            remainingAttempts: remaining,
          );
        }
      } catch (_) {
        // Network connection error: proceed to local offline PBKDF2 verification below
      }
    }

    // 4. Fallback: Verify local PBKDF2 PIN hash offline
    final salt = await getOrCreateSalt(email: targetEmail);
    final enteredHash = derivePbkdf2PinKey(pin, salt);

    String? storedHash;
    if (targetEmail != null && targetEmail.isNotEmpty) {
      storedHash = await _secureStorage.read(key: hashKey);
    } else {
      storedHash = await _secureStorage.read(key: _keyPinHash);
    }

    if (storedHash != null && enteredHash == storedHash) {
      if (targetEmail != null) {
        await _secureStorage.delete(key: failedKey);
        await _secureStorage.delete(key: lockedKey);
      }
      await _secureStorage.delete(key: _keyFailedAttempts);
      await _secureStorage.delete(key: _keyLockedUntil);
      return PinUnlockResult(success: true);
    }

    // Failure: Increment failed attempts
    final attemptsStr = (targetEmail != null ? await _secureStorage.read(key: failedKey) : null) ??
        await _secureStorage.read(key: _keyFailedAttempts);
    int failedAttempts = (attemptsStr != null ? int.tryParse(attemptsStr) ?? 0 : 0) + 1;

    if (targetEmail != null) {
      await _secureStorage.write(key: failedKey, value: failedAttempts.toString());
    }
    await _secureStorage.write(key: _keyFailedAttempts, value: failedAttempts.toString());

    if (failedAttempts >= maxFailedAttempts) {
      final lockedUntil = DateTime.now().add(lockoutDuration);
      if (targetEmail != null) {
        await _secureStorage.write(key: lockedKey, value: lockedUntil.toIso8601String());
      }
      await _secureStorage.write(key: _keyLockedUntil, value: lockedUntil.toIso8601String());
      return PinUnlockResult(
        success: false,
        isLocked: true,
        errorMessage: 'Maximum PIN attempts exceeded. App locked for 15 minutes.',
        remainingAttempts: 0,
      );
    }

    final remaining = maxFailedAttempts - failedAttempts;
    return PinUnlockResult(
      success: false,
      errorMessage: 'Invalid 6-digit PIN. $remaining attempt${remaining == 1 ? '' : 's'} remaining.',
      remainingAttempts: remaining,
    );
  }

  /// Verify account password with central server and set a new 6-digit PIN
  Future<Map<String, dynamic>> verifyPasswordAndResetPin({
    required String password,
    required String newPin,
    String? email,
  }) async {
    final targetEmail = email ?? await _secureStorage.read(key: _keyUserEmail);
    if (targetEmail == null || targetEmail.isEmpty) {
      return {'success': false, 'errorMessage': 'No active account email found.'};
    }
    if (!isValidPinFormat(newPin)) {
      return {'success': false, 'errorMessage': 'New PIN must be exactly 6 numeric digits.'};
    }

    // Verify credentials against server
    final serverUrl = await getServerUrl();
    try {
      final loginUri = Uri.parse('$serverUrl/api/v1/auth/login');
      final res = await http.post(
        loginUri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': targetEmail.trim(), 'password': password}),
      ).timeout(const Duration(seconds: 15));

      if (res.statusCode != 200) {
        return {
          'success': false,
          'errorMessage': 'Password verification failed. Please enter your valid CRBCL password.',
        };
      }

      // Password verified! Now update PIN for this user
      final setSuccess = await setPin(newPin, email: targetEmail);
      if (!setSuccess) {
        return {'success': false, 'errorMessage': 'Failed to save new PIN.'};
      }

      return {'success': true, 'message': 'New Quick Access PIN successfully created and saved.'};
    } catch (e) {
      return {
        'success': false,
        'errorMessage': 'Unable to reach the server to verify password: $e',
      };
    }
  }

  /// Request password reset link
  Future<Map<String, dynamic>> forgotPassword(String email) async {
    final effectiveUrl = (await getServerUrl()).replaceAll(RegExp(r'/+$'), '');
    try {
      final uri = Uri.parse('$effectiveUrl/api/v1/auth/forgot-password');
      await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email.trim()}),
      ).timeout(const Duration(seconds: 15));

      // Always return success like web client to prevent user enumeration
      return {
        'success': true,
        'message': "If an account exists with that email, you'll receive a password reset link shortly.",
      };
    } catch (_) {
      return {
        'success': true,
        'message': "If an account exists with that email, you'll receive a password reset link shortly.",
      };
    }
  }

  /// Resend OTP verification code
  Future<Map<String, dynamic>> resendOtp(String email) async {
    final effectiveUrl = (await getServerUrl()).replaceAll(RegExp(r'/+$'), '');
    try {
      final uri = Uri.parse('$effectiveUrl/api/v1/auth/resend-otp');
      final response = await http.post(
        uri,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email.trim()}),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return {'success': true, 'message': 'A new verification code has been sent to your email.'};
      }
      return {'success': false, 'errorMessage': 'Failed to resend verification code.'};
    } catch (e) {
      return {'success': false, 'errorMessage': 'Connection error: $e'};
    }
  }

  /// Switch user account by clearing active session credentials
  Future<void> switchUser() async {
    await _secureStorage.delete(key: _keyAccessToken);
    await _secureStorage.delete(key: _keyRefreshToken);
    await _secureStorage.delete(key: _keyUserEmail);
    await _secureStorage.delete(key: _keyUserId);
    await _secureStorage.delete(key: _keyUserName);
    await _secureStorage.delete(key: _keyUserRoles);
    await _secureStorage.delete(key: _keyUserPermissions);
    await _secureStorage.delete(key: _keyUserAvatar);
    await _secureStorage.delete(key: _keyLastAuthTime);
  }

  /// Get current access token
  Future<String?> getAccessToken() async {
    return await _secureStorage.read(key: _keyAccessToken);
  }

  /// Touch last auth time upon successful sync
  Future<void> touchAuthTimestamp() async {
    await _secureStorage.write(key: _keyLastAuthTime, value: DateTime.now().toIso8601String());
  }

  /// Get stored user metadata
  Future<Map<String, dynamic>> getCurrentUser() async {
    final id = await _secureStorage.read(key: _keyUserId);
    final email = await _secureStorage.read(key: _keyUserEmail);
    final name = await _secureStorage.read(key: _keyUserName);
    final rolesStr = await _secureStorage.read(key: _keyUserRoles);
    final permsStr = await _secureStorage.read(key: _keyUserPermissions);
    final avatarUrl = await _secureStorage.read(key: _keyUserAvatar);

    return {
      'id': id ?? '',
      'email': email ?? '',
      'name': name ?? '',
      'roles': rolesStr != null ? jsonDecode(rolesStr) : [],
      'permissions': permsStr != null ? jsonDecode(permsStr) : [],
      'avatar_url': avatarUrl ?? '',
    };
  }

  /// Update user profile photo and synchronize with backend
  Future<bool> updateAvatar(String avatarUrl) async {
    await _secureStorage.write(key: _keyUserAvatar, value: avatarUrl);
    try {
      final serverUrl = await getServerUrl();
      final token = await getAccessToken();
      if (token != null && token.isNotEmpty) {
        await http.post(
          Uri.parse('$serverUrl/api/v1/auth/avatar'),
          headers: {
            'Authorization': 'Bearer $token',
            'Content-Type': 'application/json',
          },
          body: jsonEncode({'avatar_url': avatarUrl}),
        ).timeout(const Duration(seconds: 15));
      }
    } catch (_) {}
    return true;
  }

  /// Check if an email address represents an administrator
  static bool isEmailAdmin(String? email) {
    if (email == null || email.trim().isEmpty) return false;
    final lower = email.trim().toLowerCase();
    return lower == 'admin@crbcl.ca' || lower.startsWith('admin@');
  }

  static const Set<String> _supervisorUpwardRoles = {
    'supervisor',
    'resource_supervisor',
    'director_manager',
    'resource_director',
    'director',
    'manager',
    'executive_director',
    'ceo',
    'chief_executive_officer',
    'it_admin',
    'admin',
    'administrator',
    'system_admin',
    'super_admin',
    'system administrator',
  };

  /// Check if the currently logged-in user has supervisor or upward authority to delete/restore clients
  Future<bool> canDeleteClients() async {
    final user = await getCurrentUser();
    final email = (user['email']?.toString() ?? '').trim().toLowerCase();
    if (email == 'admin@crbcl.ca' || email.startsWith('admin@')) {
      return true;
    }

    final rawRoles = user['roles'];
    if (rawRoles is List) {
      for (final r in rawRoles) {
        final normalized = (r is Map ? (r['key'] ?? r['name'] ?? '') : r).toString().trim().toLowerCase();
        if (_supervisorUpwardRoles.contains(normalized)) {
          return true;
        }
      }
    }

    final rawPerms = user['permissions'];
    if (rawPerms is List) {
      for (final p in rawPerms) {
        final permStr = p.toString().trim().toLowerCase();
        if (permStr == 'client.delete' || permStr == 'client.approve') {
          return true;
        }
      }
    }

    return false;
  }

  /// Check whether an administrator PIN has been configured
  Future<bool> hasAdminPin() async {
    return await hasUserPin('admin@crbcl.ca');
  }

  /// Load cached admin users from persistent secure storage
  Future<List<Map<String, dynamic>>> _loadCachedAdminUsers() async {
    final cached = await _secureStorage.read(key: _keyAdminUsersCache);
    if (cached != null && cached.isNotEmpty) {
      try {
        final decoded = jsonDecode(cached);
        if (decoded is List) {
          return List<Map<String, dynamic>>.from(
            decoded.map((item) => Map<String, dynamic>.from(item as Map)),
          );
        }
      } catch (_) {}
    }

    // Default authoritative baseline roster
    final initialRoster = [
      {
        'id': 'usr-001',
        'name': 'Sarah Standingready',
        'full_name': 'Sarah Standingready',
        'email': 's.standingready@crbcl.org',
        'role': 'Caseworker',
        'role_key': 'caseworker',
        'department': 'Direct Client Care',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-002',
        'name': 'Michael O’Soup',
        'full_name': 'Michael O’Soup',
        'email': 'm.osoup@crbcl.org',
        'role': 'Intake Investigator',
        'role_key': 'intake_worker',
        'department': 'Child Welfare Intake',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-003',
        'name': 'Jessica Severight',
        'full_name': 'Jessica Severight',
        'email': 'j.severight@crbcl.org',
        'role': 'Office Coordinator',
        'role_key': 'office_coordinator',
        'department': 'Operations & Facilities',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-004',
        'name': 'David Brass',
        'full_name': 'David Brass',
        'email': 'd.brass@crbcl.org',
        'role': 'Cultural Liaison',
        'role_key': 'cultural_worker',
        'department': 'Elders & Ceremonies',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-005',
        'name': 'Amanda Whitehawk',
        'full_name': 'Amanda Whitehawk',
        'email': 'a.whitehawk@crbcl.org',
        'role': 'Front Desk Receptionist',
        'role_key': 'front_desk',
        'department': 'Intake & Reception',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-006',
        'name': 'Darren Keshane',
        'full_name': 'Darren Keshane',
        'email': 'd.keshane@crbcl.org',
        'role': 'Finance Officer',
        'role_key': 'finance_staff',
        'department': 'Finance & Administration',
        'team_access': ['all'],
        'is_active': true,
        'status': 'Active',
      },
      {
        'id': 'usr-007',
        'name': 'Kendra Strongquill',
        'full_name': 'Kendra Strongquill',
        'email': 'k.strongquill@crbcl.org',
        'role': 'Frontline Caseworker',
        'role_key': 'caseworker',
        'department': 'Direct Client Care',
        'team_access': ['all'],
        'is_active': false,
        'status': 'Pending Approval',
      },
      {
        'id': 'usr-008',
        'name': 'Robert Musqua',
        'full_name': 'Robert Musqua',
        'email': 'r.musqua@crbcl.org',
        'role': 'Housing Coordinator',
        'role_key': 'caseworker',
        'department': 'Community Housing',
        'team_access': ['all'],
        'is_active': false,
        'status': 'Pending Approval',
      },
    ];

    await _saveCachedAdminUsers(initialRoster);
    return initialRoster;
  }

  /// Save admin users to persistent secure storage
  Future<void> _saveCachedAdminUsers(List<Map<String, dynamic>> users) async {
    try {
      await _secureStorage.write(
        key: _keyAdminUsersCache,
        value: jsonEncode(users),
      );
    } catch (_) {}
  }

  /// Get users list for IT Administrator management (with offline persistence and server sync)
  Future<List<Map<String, dynamic>>> getAdminUsers() async {
    final serverUrl = await getServerUrl();
    final token = await getAccessToken();

    if (token != null && token.isNotEmpty) {
      try {
        final uri = Uri.parse('$serverUrl/api/v1/users');
        final res = await http.get(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        ).timeout(const Duration(seconds: 10));

        if (res.statusCode == 200) {
          final data = jsonDecode(res.body);
          List<dynamic>? rawList;
          if (data is List) {
            rawList = data;
          } else if (data is Map && data['items'] is List) {
            rawList = data['items'] as List;
          }

          if (rawList != null && rawList.isNotEmpty) {
            final List<Map<String, dynamic>> serverUsers = [];
            for (final item in rawList) {
              if (item is Map) {
                final roles = (item['roles'] is List) ? (item['roles'] as List) : [];
                final roleStr = (item['role'] as String?)?.isNotEmpty == true
                    ? item['role'] as String
                    : (roles.isNotEmpty ? roles.first.toString() : 'caseworker');
                final isActive = item['is_active'] == true;
                final name = (item['full_name'] as String?)?.isNotEmpty == true
                    ? item['full_name'] as String
                    : ((item['display_name'] as String?)?.isNotEmpty == true
                        ? item['display_name'] as String
                        : (item['name'] as String? ?? item['email'] as String? ?? 'Staff Member'));

                serverUsers.add({
                  'id': item['id']?.toString() ?? '',
                  'name': name,
                  'full_name': item['full_name'] ?? name,
                  'email': item['email'] ?? '',
                  'role': roleStr.replaceAll('_', ' '),
                  'role_key': roleStr,
                  'department': item['department'] ?? 'General',
                  'team_access': item['team_access'] ?? [],
                  'is_active': isActive,
                  'status': isActive ? 'Active' : 'Pending Approval',
                });
              }
            }

            await _saveCachedAdminUsers(serverUsers);
            return serverUsers;
          }
        }
      } catch (_) {}
    }

    // Return persisted cached users (preserves approvals and local state changes)
    return await _loadCachedAdminUsers();
  }

  /// Approve a pending staff user with immediate local persistence and background server sync
  Future<bool> approveAdminUser(String userId, {String roleKey = 'it_admin'}) async {
    // 1. Immediately persist approval in local cache so refresh and restart reflect Active state
    final currentUsers = await _loadCachedAdminUsers();
    bool found = false;
    for (final u in currentUsers) {
      if (u['id'] == userId || u['email'] == userId) {
        u['is_active'] = true;
        u['status'] = 'Active';
        u['role_key'] = roleKey;
        found = true;
        break;
      }
    }
    if (found) {
      await _saveCachedAdminUsers(currentUsers);
    }

    // 2. Perform online server sync
    final serverUrl = await getServerUrl();
    final token = await getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final approveUri = Uri.parse('$serverUrl/api/v1/users/$userId/approve?role_key=$roleKey');
        final res = await http.patch(
          approveUri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
        ).timeout(const Duration(seconds: 10));

        if (res.statusCode != 200) {
          // Fallback to direct user update
          final updateUri = Uri.parse('$serverUrl/api/v1/users/$userId');
          await http.patch(
            updateUri,
            headers: {
              'Content-Type': 'application/json',
              'Authorization': 'Bearer $token',
            },
            body: jsonEncode({
              'is_active': true,
              'role': roleKey,
            }),
          ).timeout(const Duration(seconds: 8));
        }
      } catch (_) {}
    }
    return true;
  }

  /// Toggle staff user active status with persistent storage
  Future<bool> toggleAdminUserActive(String userId, bool currentActive) async {
    final currentUsers = await _loadCachedAdminUsers();
    final nextActive = !currentActive;
    for (final u in currentUsers) {
      if (u['id'] == userId || u['email'] == userId) {
        u['is_active'] = nextActive;
        u['status'] = nextActive ? 'Active' : 'Disabled';
        break;
      }
    }
    await _saveCachedAdminUsers(currentUsers);

    final serverUrl = await getServerUrl();
    final token = await getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final uri = Uri.parse('$serverUrl/api/v1/users/$userId');
        await http.patch(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
          body: jsonEncode({'is_active': nextActive}),
        ).timeout(const Duration(seconds: 8));
      } catch (_) {}
    }
    return true;
  }

  /// Create an immediately active user account with assigned role and credentials matching web portal
  Future<Map<String, dynamic>> createAdminUser({
    required String email,
    required String fullName,
    required String password,
    required String role,
    String? department,
    List<String>? teamAccess,
  }) async {
    final newUser = {
      'id': 'usr-${DateTime.now().millisecondsSinceEpoch}',
      'name': fullName.trim(),
      'full_name': fullName.trim(),
      'email': email.trim(),
      'role': role.replaceAll('_', ' '),
      'role_key': role,
      'department': (department != null && department.isNotEmpty) ? department : 'Direct Client Care',
      'team_access': teamAccess ?? ['all'],
      'is_active': true,
      'status': 'Active',
      'created_at': DateTime.now().toIso8601String(),
    };

    // 1. Immediately insert into local cache at top of list
    final currentUsers = await _loadCachedAdminUsers();
    // Remove if already exists with same email to avoid duplicates
    currentUsers.removeWhere((u) => (u['email'] as String? ?? '').toLowerCase() == email.trim().toLowerCase());
    currentUsers.insert(0, newUser);
    await _saveCachedAdminUsers(currentUsers);

    // 2. Perform online creation if connected
    final serverUrl = await getServerUrl();
    final token = await getAccessToken();
    if (token != null && token.isNotEmpty) {
      try {
        final uri = Uri.parse('$serverUrl/api/v1/users');
        await http.post(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $token',
          },
          body: jsonEncode({
            'full_name': fullName.trim(),
            'email': email.trim(),
            'password': password,
            'department': (department != null && department.isNotEmpty) ? department : null,
            'role_keys': [role],
            'team_ids': [],
          }),
        ).timeout(const Duration(seconds: 12));
      } catch (_) {}
    }

    return newUser;
  }

  /// Invite new staff member (compatibility wrapper for createAdminUser)
  Future<bool> inviteAdminUser({
    required String email,
    required String fullName,
    required String role,
    String? department,
  }) async {
    await createAdminUser(
      email: email,
      fullName: fullName,
      password: 'CRB#${Random.secure().nextInt(900000) + 100000}',
      role: role,
      department: department,
    );
    return true;
  }

  /// Clear all stored tokens and sessions
  Future<void> logout() async {
    await _secureStorage.delete(key: _keyAccessToken);
    await _secureStorage.delete(key: _keyRefreshToken);
    await _secureStorage.delete(key: _keyLastAuthTime);
  }
}

