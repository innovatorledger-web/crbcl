import React, { useState } from "react";
import { Outlet, Link, useLocation } from "react-router-dom";
import { 
  Shield, 
  Cpu, 
  BookOpen, 
  ArrowLeftRight, 
  LogOut, 
  Menu, 
  X, 
  ChevronLeft, 
  ChevronRight, 
  Users, 
  KeyRound, 
  Activity,
  UserCheck
} from "lucide-react";
import { api } from "@/api";
import crbclEmblem from "@/assets/crbcl-emblem.png";
import crbclLogoDark from "@/assets/crbcl-logo-dark.png";
import NotificationBell from "@/components/notifications/NotificationBell";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const ADMIN_NAV_ITEMS = [
  { label: "Admin & IT Portal", icon: Shield, path: "/admin" },
  { label: "Enterprise Integrations", icon: Cpu, path: "/admin/integrations" },
  { label: "Cultural Terminology", icon: BookOpen, path: "/admin/terminology" },
];

export default function AdminLayout() {
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const handleAdminLogout = () => {
    api.auth.logout("/admin/login");
  };

  const navContent = (
    <div className="flex flex-col h-full bg-[#1A1311] text-[#E8E3DF]">
      {/* Brand Header */}
      <div className="p-3 border-b border-white/10 flex flex-col items-center justify-center min-h-[72px]">
        <Link
          to="/admin"
          className="group focus:outline-none flex flex-col items-center justify-center w-full"
          title="CRBCL IT Administration"
        >
          {collapsed ? (
            <img
              src={crbclEmblem}
              alt="Chief Red Bear Children's Lodge"
              className="w-10 h-10 object-contain mx-auto transition-transform group-hover:scale-110"
            />
          ) : (
            <div className="flex flex-col items-center text-center">
              <img
                src={crbclLogoDark}
                alt="Chief Red Bear Children's Lodge"
                className="h-12 w-auto max-w-[180px] object-contain mx-auto"
              />
              <span className="mt-1 px-2 py-0.5 text-[10px] uppercase font-bold tracking-wider rounded bg-purple-900/60 text-purple-300 border border-purple-700/40">
                IT Admin Portal
              </span>
            </div>
          )}
        </Link>
      </div>

      {/* Admin Nav Items */}
      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        <div className={`text-[10px] uppercase tracking-wider font-semibold text-white/40 px-3 py-1 mb-1 ${collapsed ? 'hidden' : 'block'}`}>
          Admin Governance
        </div>

        {ADMIN_NAV_ITEMS.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setMobileOpen(false)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 group ${
                isActive
                  ? "bg-purple-800 text-white shadow-md font-semibold"
                  : "text-white/80 hover:bg-white/10 hover:text-white"
              }`}
            >
              <item.icon className={`w-[18px] h-[18px] flex-shrink-0 ${isActive ? "text-purple-200" : "text-white/60 group-hover:text-white"}`} />
              {!collapsed && <span className="truncate">{item.label}</span>}
            </Link>
          );
        })}

        <div className="my-4 border-t border-white/10" />

        <div className={`text-[10px] uppercase tracking-wider font-semibold text-white/40 px-3 py-1 mb-1 ${collapsed ? 'hidden' : 'block'}`}>
          Cross-Platform Switch
        </div>

        <Link
          to="/"
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-amber-300 hover:bg-amber-500/10 transition-colors"
          title="Switch to Staff Platform"
        >
          <ArrowLeftRight className="w-[18px] h-[18px] flex-shrink-0 text-amber-400" />
          {!collapsed && <span>Staff Platform</span>}
        </Link>
      </nav>

      {/* Admin Sign Out Footer */}
      <div className="p-3 border-t border-white/10">
        <button
          onClick={handleAdminLogout}
          className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-300 hover:bg-red-500/15 hover:text-red-200 w-full transition-colors cursor-pointer"
        >
          <LogOut className="w-[18px] h-[18px] flex-shrink-0" />
          {!collapsed && <span>Sign Out of Admin</span>}
        </button>
      </div>
    </div>
  );

  return (
    <div className="flex min-h-screen bg-background">
      {/* Mobile toggle */}
      <button 
        className="lg:hidden fixed top-4 left-4 z-50 p-2 bg-purple-800 text-white rounded-lg shadow-lg"
        onClick={() => setMobileOpen(!mobileOpen)}
      >
        {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
      </button>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/60 z-40"
          onClick={() => setMobileOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <aside className={`lg:hidden fixed top-0 left-0 h-full w-64 bg-[#1A1311] z-50 transform transition-transform duration-300 ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}>
        {navContent}
      </aside>

      {/* Desktop sidebar */}
      <aside className={`hidden lg:flex flex-col bg-[#1A1311] border-r border-white/10 transition-all duration-300 ${collapsed ? "w-[68px]" : "w-64"} relative h-screen sticky top-0`}>
        {navContent}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="absolute -right-3 top-20 w-6 h-6 bg-purple-700 text-white rounded-full flex items-center justify-center shadow-md hover:scale-110 transition-transform cursor-pointer"
        >
          {collapsed ? <ChevronRight className="w-3 h-3" /> : <ChevronLeft className="w-3 h-3" />}
        </button>
      </aside>

      {/* Main Admin Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <header className="h-14 border-b border-border pl-16 pr-4 lg:px-8 flex items-center justify-between bg-card/60 backdrop-blur-sm sticky top-0 z-30">
          <div className="flex items-center gap-2.5">
            <Link to="/admin" className="flex items-center gap-2.5 group focus:outline-none">
              <img
                src={crbclEmblem}
                alt="Chief Red Bear Children's Lodge"
                className="w-6 h-6 object-contain"
              />
              <span className="text-xs font-semibold text-foreground uppercase tracking-wider hidden sm:inline">
                Chief Red Bear Children's Lodge • IT Administration & Governance Portal
              </span>
              <span className="text-xs font-semibold text-foreground uppercase tracking-wider sm:hidden">
                CRBCL Admin
              </span>
            </Link>
          </div>

          <div className="flex items-center gap-2 sm:gap-3">
            <NotificationBell />
            <div className="h-5 w-px bg-border/60" />

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <button
                  type="button"
                  className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-muted transition-colors cursor-pointer"
                >
                  <Avatar className="h-8 w-8 ring-2 ring-purple-600/30">
                    <AvatarFallback className="bg-purple-800 text-white font-bold text-xs">
                      IT
                    </AvatarFallback>
                  </Avatar>
                  <div className="hidden sm:flex flex-col items-start text-left leading-none">
                    <span className="text-xs font-bold text-foreground">IT Administrator</span>
                    <span className="text-[10px] text-purple-600 dark:text-purple-400 font-semibold mt-0.5">admin@crbcl.ca</span>
                  </div>
                </button>
              </DropdownMenuTrigger>

              <DropdownMenuContent className="w-56" align="end">
                <DropdownMenuLabel>
                  <div className="text-xs font-bold">CRBCL System Administration</div>
                  <div className="text-[11px] text-muted-foreground">admin@crbcl.ca</div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem asChild>
                  <Link to="/admin" className="cursor-pointer">
                    <Shield className="w-4 h-4 mr-2 text-purple-600" />
                    Admin & IT Dashboard
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuItem asChild>
                  <Link to="/" className="cursor-pointer">
                    <ArrowLeftRight className="w-4 h-4 mr-2 text-amber-500" />
                    Switch to Staff Platform
                  </Link>
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem
                  onClick={handleAdminLogout}
                  className="cursor-pointer text-destructive focus:text-destructive focus:bg-destructive/10"
                >
                  <LogOut className="w-4 h-4 mr-2" />
                  Sign Out of Admin
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        <main className="flex-1 overflow-x-hidden">
          <div className="p-3 sm:p-4 lg:p-8 max-w-[1400px]">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
