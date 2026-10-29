import React, { useState, useEffect, useRef } from "react";
import { api } from "@/api";
import PageHeader from "@/components/shared/PageHeader";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { toast } from "@/components/ui/use-toast";
import {
  User,
  Lock,
  Camera,
  Shield,
  Mail,
  CheckCircle2,
  AlertCircle,
  Eye,
  EyeOff,
  Loader2,
  Users,
  Trash2,
  Palette,
  KeyRound,
} from "lucide-react";
import AppearanceSettings from "@/components/settings/AppearanceSettings";

export default function Profile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Profile fields state
  const [fullName, setFullName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [phone, setPhone] = useState("");
  const [avatarUrl, setAvatarUrl] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);

  // 6-Digit PIN fields state
  const [pin, setPin] = useState("");
  const [confirmPin, setConfirmPin] = useState("");
  const [showPin, setShowPin] = useState(false);
  const [savingPin, setSavingPin] = useState(false);
  const [pinError, setPinError] = useState("");
  const [pinSuccess, setPinSuccess] = useState(false);

  // Password fields state
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [passwordError, setPasswordError] = useState("");

  const fileInputRef = useRef(null);

  const loadUserData = async () => {
    try {
      setLoading(true);
      const data = await api.auth.me();
      if (data) {
        setUser(data);
        setFullName(data.full_name || "");
        setDisplayName(data.display_name || "");
        setPhone(data.phone || "");
        setAvatarUrl(data.avatar_url || "");
      }
    } catch (err) {
      console.warn("Failed to load user profile:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUserData();
  }, []);

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

  // Handle saving profile changes
  const handleSaveProfile = async (e) => {
    e?.preventDefault();
    if (!fullName.trim()) {
      toast({
        title: "Name required",
        description: "Please enter your full name.",
        variant: "destructive",
      });
      return;
    }

    setSavingProfile(true);
    try {
      const updated = await api.auth.updateProfile({
        full_name: fullName.trim(),
        display_name: displayName.trim() || null,
        phone: phone.trim() || null,
        avatar_url: avatarUrl || null,
      });

      setUser(updated);
      // Dispatch custom event to notify UserNav and other components immediately
      window.dispatchEvent(new Event("crbcl_profile_updated"));

      toast({
        title: "Profile Updated",
        description: "Your profile information has been saved successfully.",
      });
    } catch (err) {
      toast({
        title: "Update Failed",
        description: err.message || "Failed to update profile.",
        variant: "destructive",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  // Helper to resize/compress avatar image to lightweight, sharp WebP/JPEG data URL (~40KB)
  const compressImage = (file, maxWidth = 400, maxHeight = 400, quality = 0.85) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
          let width = img.width;
          let height = img.height;
          if (width > height) {
            if (width > maxWidth) {
              height = Math.round((height * maxWidth) / width);
              width = maxWidth;
            }
          } else {
            if (height > maxHeight) {
              width = Math.round((width * maxHeight) / height);
              height = maxHeight;
            }
          }
          const canvas = document.createElement("canvas");
          canvas.width = width;
          canvas.height = height;
          const ctx = canvas.getContext("2d");
          ctx.drawImage(img, 0, 0, width, height);
          resolve(canvas.toDataURL("image/jpeg", quality));
        };
        img.onerror = reject;
        img.src = e.target.result;
      };
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  };

  // Handle avatar photo selection, conversion, and instant automatic save
  const handleFileChange = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith("image/")) {
      toast({
        title: "Invalid file type",
        description: "Please select an image file (PNG, JPG, WebP).",
        variant: "destructive",
      });
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please upload an image smaller than 10MB.",
        variant: "destructive",
      });
      return;
    }

    setSavingProfile(true);
    try {
      const compressedData = await compressImage(file, 400, 400, 0.85);
      setAvatarUrl(compressedData);

      // Instantly persist to backend so refresh retains the photo 100%
      const updated = await api.auth.updateProfile({
        full_name: fullName.trim() || user?.full_name,
        display_name: displayName.trim() || user?.display_name || null,
        phone: phone.trim() || user?.phone || null,
        avatar_url: compressedData,
      });

      setUser(updated);
      window.dispatchEvent(new Event("crbcl_profile_updated"));

      toast({
        title: "Profile Photo Saved",
        description: "Your profile picture has been updated and synchronized.",
      });
    } catch (err) {
      console.error("Failed to save avatar photo:", err);
      toast({
        title: "Upload Failed",
        description: err.message || "Could not save profile photo. Please try again.",
        variant: "destructive",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  // Handle removing profile photo with instant auto-save
  const handleRemovePhoto = async () => {
    setSavingProfile(true);
    setAvatarUrl("");
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
    try {
      const updated = await api.auth.updateProfile({
        full_name: fullName.trim() || user?.full_name,
        display_name: displayName.trim() || user?.display_name || null,
        phone: phone.trim() || user?.phone || null,
        avatar_url: null,
      });
      setUser(updated);
      window.dispatchEvent(new Event("crbcl_profile_updated"));
      toast({
        title: "Profile Photo Removed",
        description: "Your profile picture has been cleared.",
      });
    } catch (err) {
      toast({
        title: "Failed to Remove Photo",
        description: err.message || "Could not clear photo.",
        variant: "destructive",
      });
    } finally {
      setSavingProfile(false);
    }
  };

  // Handle password change
  const handleChangePassword = async (e) => {
    e?.preventDefault();
    setPasswordError("");

    if (!currentPassword) {
      setPasswordError("Please enter your current password.");
      return;
    }
    if (newPassword.length < 8) {
      setPasswordError("New password must be at least 8 characters.");
      return;
    }
    if (newPassword !== confirmPassword) {
      setPasswordError("New password and confirm password do not match.");
      return;
    }

    setSavingPassword(true);
    try {
      await api.auth.changePassword({
        currentPassword,
        newPassword,
      });

      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");

      toast({
        title: "Password Changed",
        description: "Your password has been updated. Please remember your new password.",
      });
    } catch (err) {
      setPasswordError(err.message || "Failed to change password. Please verify current password.");
      toast({
        title: "Password Change Failed",
        description: err.message || "Current password incorrect.",
        variant: "destructive",
      });
    } finally {
      setSavingPassword(false);
    }
  };

  // Handle 6-digit PIN change
  const handleSavePin = async (e) => {
    e?.preventDefault();
    setPinError("");
    setPinSuccess(false);

    if (pin.length !== 6 || !/^\d{6}$/.test(pin)) {
      setPinError("PIN must be exactly 6 numeric digits.");
      return;
    }
    if (pin !== confirmPin) {
      setPinError("PIN and confirm PIN do not match.");
      return;
    }

    setSavingPin(true);
    try {
      await api.auth.setPin(pin);
      setPinSuccess(true);
      setPin("");
      setConfirmPin("");
      toast({
        title: "6-Digit PIN Updated",
        description: "Your PIN is now synchronized for instant login across website and mobile app.",
      });
    } catch (err) {
      setPinError(err.message || "Failed to update 6-digit PIN.");
      toast({
        title: "PIN Update Failed",
        description: err.message || "Failed to save PIN.",
        variant: "destructive",
      });
    } finally {
      setSavingPin(false);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-24 space-y-4">
        <div className="w-10 h-10 border-4 border-primary/20 border-t-primary rounded-full animate-spin" />
        <p className="text-sm text-muted-foreground">Loading your profile...</p>
      </div>
    );
  }

  const initials = getInitials(fullName || user?.full_name, user?.email);
  const roles = Array.isArray(user?.roles) ? user.roles : (user?.role ? [user.role] : []);
  const teamAccess = Array.isArray(user?.team_access) ? user.team_access : [];

  return (
    <div className="space-y-6 max-w-5xl mx-auto pb-12">
      <PageHeader
        title="My Profile & Settings"
        subtitle="Manage your personal details, secure login credentials, and account permissions"
      />

      {/* Hero Profile Overview Card */}
      <Card className="border shadow-sm overflow-hidden bg-gradient-to-r from-card to-muted/30">
        <CardContent className="p-6">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6 text-center sm:text-left">
            {/* Avatar with quick change overlay */}
            <div className="relative group">
              <Avatar className="h-24 w-24 sm:h-28 sm:sm-28 ring-4 ring-background shadow-md">
                {avatarUrl ? (
                  <AvatarImage src={avatarUrl} alt={fullName} className="object-cover" />
                ) : null}
                <AvatarFallback className="bg-primary/10 text-primary font-bold text-2xl sm:text-3xl">
                  {initials}
                </AvatarFallback>
              </Avatar>

              {savingProfile && (
                <div className="absolute inset-0 bg-black/40 rounded-full flex items-center justify-center pointer-events-none z-10">
                  <Loader2 className="w-6 h-6 text-white animate-spin" />
                </div>
              )}

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                disabled={savingProfile}
                aria-label="Upload photo"
                className="absolute bottom-0 right-0 p-2 rounded-full bg-primary text-primary-foreground shadow-md hover:bg-primary/90 transition-transform active:scale-95 cursor-pointer z-20"
              >
                {savingProfile ? <Loader2 className="w-4 h-4 animate-spin" /> : <Camera className="w-4 h-4" />}
              </button>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>

            {/* Profile Info Summary */}
            <div className="space-y-2 flex-1 min-w-0">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                <div className="min-w-0">
                  <h2 className="text-2xl font-bold tracking-tight text-foreground truncate">
                    {fullName || "Team Member"}
                  </h2>
                  <p className="text-sm text-muted-foreground flex items-center justify-center sm:justify-start gap-1.5 mt-0.5">
                    <Mail className="w-3.5 h-3.5 flex-shrink-0" />
                    <span className="truncate">{user?.email}</span>
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 ml-1" />
                  </p>
                </div>
              </div>

              {/* Roles Badges - Strictly IT Admin, Executive Director, CEO */}
              <div className="flex flex-wrap items-center justify-center sm:justify-start gap-1.5 pt-1">
                {roles
                  .filter((r) => ["it_admin", "executive_director", "ceo", "admin"].includes(String(r).toLowerCase()))
                  .map((r) => {
                    const key = String(r).toLowerCase();
                    const label = key === "it_admin" || key === "admin" ? "IT Admin" : key === "ceo" ? "CEO" : "Executive Director";
                    return (
                      <span
                        key={key}
                        className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-primary/10 text-primary border border-primary/20"
                      >
                        <Shield className="w-3 h-3" />
                        {label}
                      </span>
                    );
                  })}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Profile Management Tabs */}
      <Tabs defaultValue={new URLSearchParams(window.location.search).get("tab") || "details"} className="space-y-6">
        <TabsList className="grid grid-cols-4 w-full sm:w-[560px] p-1 bg-muted/60">
          <TabsTrigger value="details" className="text-xs sm:text-sm">
            <User className="w-4 h-4 mr-1.5 hidden sm:inline" />
            Information
          </TabsTrigger>
          <TabsTrigger value="avatar" className="text-xs sm:text-sm">
            <Camera className="w-4 h-4 mr-1.5 hidden sm:inline" />
            Photo
          </TabsTrigger>
          <TabsTrigger value="appearance" className="text-xs sm:text-sm">
            <Palette className="w-4 h-4 mr-1.5 hidden sm:inline" />
            Appearance
          </TabsTrigger>
          <TabsTrigger value="security" className="text-xs sm:text-sm">
            <Lock className="w-4 h-4 mr-1.5 hidden sm:inline" />
            Password
          </TabsTrigger>
        </TabsList>

        {/* Tab 1: Personal Details */}
        <TabsContent value="details">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Personal Information</CardTitle>
              <CardDescription>
                Update your contact details and how your name appears across the lodge software.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveProfile} className="space-y-5">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="full_name">Full Name *</Label>
                    <Input
                      id="full_name"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      placeholder="e.g. Sarah Bear"
                      required
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="display_name">
                      Display / Short Name
                      <span className="text-xs text-muted-foreground ml-1">(optional)</span>
                    </Label>
                    <Input
                      id="display_name"
                      value={displayName}
                      onChange={(e) => setDisplayName(e.target.value)}
                      placeholder="e.g. Sarah"
                    />
                  </div>
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input
                      id="email"
                      value={user?.email || ""}
                      disabled
                      className="bg-muted text-muted-foreground cursor-not-allowed"
                    />
                    <p className="text-[11px] text-muted-foreground">
                      Contact an Executive Director or IT Admin to change your official email address.
                    </p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="phone">Phone / Contact Number</Label>
                    <Input
                      id="phone"
                      value={phone}
                      onChange={(e) => setPhone(e.target.value)}
                      placeholder="e.g. (306) 555-0199"
                    />
                  </div>
                </div>

                <div className="pt-3 flex justify-end">
                  <Button type="submit" disabled={savingProfile} className="min-w-[130px]">
                    {savingProfile ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Saving...
                      </>
                    ) : (
                      "Save Changes"
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 2: Profile Photo / Avatar */}
        <TabsContent value="avatar">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Profile Photo</CardTitle>
              <CardDescription>
                Upload an official photo or avatar. It will be displayed on case files, team rosters, and the top-right navigation bar.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex flex-col sm:flex-row items-center gap-6">
                <Avatar className="h-32 w-32 ring-4 ring-muted shadow-sm">
                  {avatarUrl ? (
                    <AvatarImage src={avatarUrl} alt={fullName} className="object-cover" />
                  ) : null}
                  <AvatarFallback className="bg-primary/10 text-primary font-bold text-4xl">
                    {initials}
                  </AvatarFallback>
                </Avatar>

                <div className="space-y-3 text-center sm:text-left">
                  <div className="flex flex-wrap gap-2 justify-center sm:justify-start">
                    <Button
                      type="button"
                      variant="outline"
                      onClick={() => fileInputRef.current?.click()}
                    >
                      <Camera className="w-4 h-4 mr-2" />
                      Choose Image...
                    </Button>

                    {avatarUrl && (
                      <Button
                        type="button"
                        variant="destructive"
                        onClick={handleRemovePhoto}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Remove Photo
                      </Button>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground">
                    Supported formats: PNG, JPG, WebP. Recommended size: 400x400 pixels (Max 4MB).
                  </p>
                </div>
              </div>

              {/* Direct Image URL input */}
              <div className="space-y-2 pt-2 border-t">
                <Label htmlFor="avatar_url" className="text-xs text-muted-foreground">
                  Or enter external image URL
                </Label>
                <div className="flex gap-2">
                  <Input
                    id="avatar_url"
                    value={avatarUrl.startsWith("data:") ? "" : avatarUrl}
                    onChange={(e) => setAvatarUrl(e.target.value)}
                    placeholder="https://example.com/photo.jpg"
                    className="text-xs"
                  />
                  {avatarUrl && !avatarUrl.startsWith("data:") && (
                    <Button
                      type="button"
                      variant="ghost"
                      size="sm"
                      onClick={() => setAvatarUrl("")}
                    >
                      Clear
                    </Button>
                  )}
                </div>
              </div>

              <div className="pt-3 flex justify-end">
                <Button
                  type="button"
                  onClick={handleSaveProfile}
                  disabled={savingProfile}
                  className="min-w-[130px]"
                >
                  {savingProfile ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Updating...
                    </>
                  ) : (
                    "Save Photo"
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Security & Password */}
        <TabsContent value="security" className="space-y-6">
          {/* Quick-Access 6-Digit PIN Card */}
          <Card>
            <CardHeader>
              <div className="flex items-center gap-2">
                <KeyRound className="w-5 h-5 text-primary" />
                <CardTitle className="text-lg">Quick-Access 6-Digit PIN</CardTitle>
              </div>
              <CardDescription>
                Set or change your 6-digit PIN. Changing it here synchronizes instantly with your CRBCL Mobile app and vice versa.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSavePin} className="space-y-4 max-w-md">
                {pinError && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{pinError}</span>
                  </div>
                )}
                {pinSuccess && (
                  <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-md flex items-center gap-2 text-emerald-800 text-sm">
                    <CheckCircle2 className="w-4 h-4 flex-shrink-0 text-emerald-600" />
                    <span>6-digit PIN successfully updated and synchronized across all platforms.</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="quick_pin">New 6-Digit PIN *</Label>
                  <div className="relative">
                    <Input
                      id="quick_pin"
                      type={showPin ? "text" : "password"}
                      inputMode="numeric"
                      pattern="[0-9]*"
                      maxLength={6}
                      value={pin}
                      onChange={(e) => setPin(e.target.value.replace(/\D/g, "").slice(0, 6))}
                      placeholder="••••••"
                      className="tracking-widest font-mono text-center text-lg pr-10"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowPin(!showPin)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showPin ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                  <p className="text-[11px] text-muted-foreground">
                    Must be exactly 6 numeric digits.
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_quick_pin">Confirm 6-Digit PIN *</Label>
                  <Input
                    id="confirm_quick_pin"
                    type={showPin ? "text" : "password"}
                    inputMode="numeric"
                    pattern="[0-9]*"
                    maxLength={6}
                    value={confirmPin}
                    onChange={(e) => setConfirmPin(e.target.value.replace(/\D/g, "").slice(0, 6))}
                    placeholder="••••••"
                    className="tracking-widest font-mono text-center text-lg"
                    required
                  />
                  {pin && confirmPin && (
                    <p
                      className={`text-xs flex items-center gap-1 ${
                        pin === confirmPin ? "text-emerald-600" : "text-destructive"
                      }`}
                    >
                      {pin === confirmPin ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          PINs match
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-3.5 h-3.5" />
                          PINs do not match
                        </>
                      )}
                    </p>
                  )}
                </div>

                <div className="pt-2 flex justify-end">
                  <Button
                    type="submit"
                    disabled={savingPin || pin.length !== 6 || confirmPin.length !== 6}
                    className="min-w-[150px]"
                  >
                    {savingPin ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Synchronizing...
                      </>
                    ) : (
                      <>
                        <KeyRound className="w-4 h-4 mr-2" />
                        Save 6-Digit PIN
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Change Password Card */}
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Change Password</CardTitle>
              <CardDescription>
                Ensure your account is using a secure password with at least 8 characters.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
                {passwordError && (
                  <div className="p-3 bg-destructive/10 border border-destructive/20 rounded-md flex items-center gap-2 text-destructive text-sm">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{passwordError}</span>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="current_password">Current Password *</Label>
                  <div className="relative">
                    <Input
                      id="current_password"
                      type={showCurrentPassword ? "text" : "password"}
                      value={currentPassword}
                      onChange={(e) => setCurrentPassword(e.target.value)}
                      placeholder="Enter current password"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showCurrentPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="new_password">New Password *</Label>
                  <div className="relative">
                    <Input
                      id="new_password"
                      type={showNewPassword ? "text" : "password"}
                      value={newPassword}
                      onChange={(e) => setNewPassword(e.target.value)}
                      placeholder="Minimum 8 characters"
                      required
                    />
                    <button
                      type="button"
                      onClick={() => setShowNewPassword(!showNewPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      {showNewPassword ? (
                        <EyeOff className="w-4 h-4" />
                      ) : (
                        <Eye className="w-4 h-4" />
                      )}
                    </button>
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm_password">Confirm New Password *</Label>
                  <Input
                    id="confirm_password"
                    type={showNewPassword ? "text" : "password"}
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    placeholder="Repeat new password"
                    required
                  />
                  {newPassword && confirmPassword && (
                    <p
                      className={`text-xs flex items-center gap-1 ${
                        newPassword === confirmPassword ? "text-emerald-600" : "text-destructive"
                      }`}
                    >
                      {newPassword === confirmPassword ? (
                        <>
                          <CheckCircle2 className="w-3.5 h-3.5" />
                          Passwords match
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-3.5 h-3.5" />
                          Passwords do not match
                        </>
                      )}
                    </p>
                  )}
                </div>

                <div className="pt-3 flex justify-end">
                  <Button
                    type="submit"
                    disabled={savingPassword || !currentPassword || !newPassword}
                    className="min-w-[150px]"
                  >
                    {savingPassword ? (
                      <>
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        Changing...
                      </>
                    ) : (
                      "Update Password"
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Tab 3: Appearance & Personalization */}
        <TabsContent value="appearance">
          <AppearanceSettings />
        </TabsContent>
      </Tabs>
    </div>
  );
}
