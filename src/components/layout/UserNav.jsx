import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { api } from "@/api";
import {
  User,
  LogOut,
  ChevronDown,
  Palette,
} from "lucide-react";

export default function UserNav() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);

  const loadUser = () => {
    // 1. Try local storage first for instantaneous render without flash
    try {
      const stored = localStorage.getItem("crbcl_current_user");
      if (stored) {
        setUser(JSON.parse(stored));
      }
    } catch {}

    // 2. Fetch fresh user state from server
    api.auth
      .me()
      .then((fresh) => {
        if (fresh) setUser(fresh);
      })
      .catch(() => {});
  };

  useEffect(() => {
    loadUser();

    // Listen to custom storage update events if profile changes in another component
    const handleProfileUpdate = () => loadUser();
    window.addEventListener("crbcl_profile_updated", handleProfileUpdate);
    window.addEventListener("storage", handleProfileUpdate);
    return () => {
      window.removeEventListener("crbcl_profile_updated", handleProfileUpdate);
      window.removeEventListener("storage", handleProfileUpdate);
    };
  }, []);

  const roles = Array.isArray(user?.roles) ? user.roles : (user?.role ? [user.role] : []);
  const normalizedRoles = roles.map((r) => (typeof r === "string" ? r : (r?.key || r?.name || r?.role || ""))).map((r) => String(r).toLowerCase().trim());
  const email = String(user?.email || "").toLowerCase().trim();

  const isItAdmin =
    email === "admin@crbcl.ca" ||
    email.includes("admin") ||
    user?.role === "admin" ||
    user?.role === "it_admin" ||
    normalizedRoles.includes("admin") ||
    normalizedRoles.includes("it_admin") ||
    normalizedRoles.includes("administrator") ||
    normalizedRoles.includes("system administrator");

  const getInitials = (name, email) => {
    if (name && name.trim()) {
      const parts = name.trim().split(/\s+/);
      if (parts.length >= 2) {
        return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
      }
      return parts[0].substring(0, 2).toUpperCase();
    }
    if (email && email.includes("@")) {
      return email.substring(0, 2).toUpperCase();
    }
    return "CB";
  };

  const getFirstName = () => {
    if (user?.display_name) return user.display_name.split(" ")[0];
    if (user?.full_name) return user.full_name.split(" ")[0];
    if (user?.email) return user.email.split("@")[0];
    return "User";
  };

  const getRoleLabel = () => {
    if (isItAdmin) return "IT Admin";
    if (roles.includes("ceo")) return "CEO";
    if (roles.includes("executive_director")) return "Executive Director";
    return "IT Admin";
  };

  const initials = getInitials(user?.full_name || user?.display_name, user?.email);
  const firstName = getFirstName();
  const roleLabel = getRoleLabel();

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <button
          type="button"
          aria-label="User profile menu"
          className="flex items-center gap-2 p-1.5 rounded-full sm:rounded-lg hover:bg-muted/80 transition-colors focus:outline-none focus:ring-2 focus:ring-primary/20 cursor-pointer select-none"
        >
          <Avatar className="h-8 w-8 ring-2 ring-primary/10 transition-transform active:scale-95">
            {user?.avatar_url && (
              <AvatarImage
                src={user.avatar_url}
                alt={user.full_name || "Profile"}
                className="object-cover"
              />
            )}
            <AvatarFallback className="bg-primary/10 text-primary font-semibold text-xs">
              {initials}
            </AvatarFallback>
          </Avatar>

          <div className="hidden sm:flex flex-col items-start text-left leading-none max-w-[130px]">
            <span className="text-xs font-semibold text-foreground truncate w-full">
              {firstName}
            </span>
            <span className="text-[10px] text-muted-foreground capitalize truncate w-full mt-0.5">
              {roleLabel}
            </span>
          </div>

          <ChevronDown className="h-3.5 w-3.5 text-muted-foreground opacity-60 hidden sm:block ml-0.5" />
        </button>
      </DropdownMenuTrigger>

      <DropdownMenuContent className="w-56" align="end" forceMount>
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-semibold leading-none truncate">
              {user?.full_name || firstName}
            </p>
            <p className="text-xs text-muted-foreground leading-none truncate">
              {user?.email || "staff@crbcl.ca"}
            </p>
            <div className="pt-1">
              <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-medium bg-primary/10 text-primary">
                {roleLabel}
              </span>
            </div>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => navigate("/profile")}
          className="cursor-pointer"
        >
          <User className="mr-2 h-4 w-4 text-muted-foreground" />
          <span>My Profile & Settings</span>
        </DropdownMenuItem>

        <DropdownMenuItem
          onClick={() => navigate("/profile?tab=appearance")}
          className="cursor-pointer"
        >
          <Palette className="mr-2 h-4 w-4 text-muted-foreground" />
          <span>Appearance & Theme</span>
        </DropdownMenuItem>


        <DropdownMenuSeparator />

        <DropdownMenuItem
          onClick={() => api.auth.logout((isItAdmin || window.location.pathname.startsWith("/admin")) ? "/admin/login" : "/login")}
          className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
        >
          <LogOut className="mr-2 h-4 w-4" />
          <span>Sign Out</span>
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
