import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';
import '../services/theme_service.dart';
import '../widgets/crbcl_logo.dart';
import '../widgets/google_icon.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _authService = MobileAuthService.instance;

  // Controllers
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _pinController = TextEditingController();
  final _newPinController = TextEditingController();
  final _confirmPinController = TextEditingController();

  bool _isLoading = true;
  bool _isOnlineLoginMode = false;
  bool _isSettingUpPin = false;

  // Visibility toggles
  bool _obscurePassword = true;
  bool _obscurePin = true;
  bool _obscureNewPin = true;
  bool _obscureConfirmPin = true;

  String? _statusMessage;
  String? _errorMessage;
  String? _activeUserEmail;
  String? _activeUserName;

  @override
  void initState() {
    super.initState();
    _checkInitialState();
  }

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _pinController.dispose();
    _newPinController.dispose();
    _confirmPinController.dispose();
    super.dispose();
  }

  Future<void> _checkInitialState() async {
    setState(() => _isLoading = true);
    final activeEmail = await _authService.getActiveUserEmail();
    final activeName = await _authService.getActiveUserName();
    final isAdmin = MobileAuthService.isEmailAdmin(activeEmail);

    // If previous user was Admin, do not offer frontline staff PIN unlock!
    final hasCreds = !isAdmin && await _authService.hasSavedCredentials(email: activeEmail);

    setState(() {
      _activeUserEmail = isAdmin ? null : activeEmail;
      _activeUserName = isAdmin ? null : activeName;
      _isOnlineLoginMode = !hasCreds;
      _isLoading = false;
    });
  }

  Future<void> _handleGoogleAuth() async {
    try {
      final serverUrl = await _authService.getServerUrl();
      final uri = Uri.parse('$serverUrl/api/v1/auth/oauth/google?returnTo=/');
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Opening Google Authentication in browser...')),
          );
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not open browser: $e')),
        );
      }
    }
  }

  Future<void> _handleOnlineLogin() async {
    final email = _emailController.text.trim();
    final password = _passwordController.text;

    if (email.isEmpty || password.isEmpty) {
      setState(() => _errorMessage = 'Please enter both email and password.');
      return;
    }

    if (MobileAuthService.isEmailAdmin(email)) {
      setState(() => _errorMessage = 'Administrator accounts cannot sign in through this portal. Please use the IT Admin Portal.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _statusMessage = 'Connecting to CRBCL backend...';
    });

    final result = await _authService.loginOnline(
      email: email,
      password: password,
      isStaffPortalOnly: true,
    );

    setState(() => _isLoading = false);

    if (!result.success) {
      setState(() => _errorMessage = result.errorMessage ?? 'Authentication failed.');
      return;
    }

    if (result.requiresPinSetup) {
      setState(() {
        _isSettingUpPin = true;
        _activeUserEmail = email;
        _statusMessage = 'Authentication successful! Please set your Quick Access PIN.';
      });
    } else {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    }
  }

  Future<void> _handleSetPin() async {
    final pin = _newPinController.text.trim();
    final confirm = _confirmPinController.text.trim();

    if (pin.length != 6 || !RegExp(r'^\d{6}$').hasMatch(pin)) {
      setState(() => _errorMessage = 'PIN must be exactly 6 numeric digits.');
      return;
    }

    if (pin != confirm) {
      setState(() => _errorMessage = 'PINs do not match. Please re-enter.');
      return;
    }

    setState(() => _isLoading = true);
    final success = await _authService.setPin(pin, email: _activeUserEmail);
    setState(() => _isLoading = false);

    if (success) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Quick Access PIN saved securely.')),
        );
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } else {
      setState(() => _errorMessage = 'Failed to derive PBKDF2 key for PIN.');
    }
  }

  Future<void> _handlePinUnlock() async {
    final pin = _pinController.text.trim();
    if (pin.length != 6 || !RegExp(r'^\d{6}$').hasMatch(pin)) {
      setState(() => _errorMessage = 'Please enter a valid 6-digit PIN.');
      return;
    }

    final targetEmail = (_activeUserEmail?.isNotEmpty == true)
        ? _activeUserEmail!
        : _emailController.text.trim();

    if (targetEmail.isEmpty) {
      setState(() => _errorMessage = 'Please enter your Staff Work Email to unlock with PIN.');
      return;
    }

    if (MobileAuthService.isEmailAdmin(targetEmail)) {
      setState(() => _errorMessage = 'Administrator accounts cannot unlock standard field operations. Please use the IT Admin Portal.');
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await _authService.unlockWithPin(pin, email: targetEmail);
    setState(() => _isLoading = false);

    if (result.success) {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } else {
      if (result.isExpired) {
        setState(() {
          _isOnlineLoginMode = true;
          _errorMessage = result.errorMessage;
        });
      } else {
        setState(() => _errorMessage = result.errorMessage);
      }
    }
  }

  Future<void> _handleSwitchUser() async {
    await _authService.switchUser();
    setState(() {
      _isOnlineLoginMode = true;
      _activeUserEmail = null;
      _activeUserName = null;
      _errorMessage = null;
      _statusMessage = null;
      _pinController.clear();
      _emailController.clear();
      _passwordController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    if (_isLoading) {
      return Scaffold(
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CrbclLogo(height: 56, variant: CrbclLogoVariant.emblem),
              const SizedBox(height: 24),
              CircularProgressIndicator(color: colorScheme.primary),
              const SizedBox(height: 12),
              Text(
                'Securing Connection...',
                style: TextStyle(
                  fontSize: 13,
                  color: colorScheme.onSurface.withValues(alpha: 0.7),
                ),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: isDark ? colorScheme.surface : const Color(0xFFF7F5F2),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 440),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Official CRBCL Brand Header
                  Center(
                    child: Column(
                      children: [
                        const CrbclLogo(
                          height: 70,
                          variant: CrbclLogoVariant.emblem,
                        ),
                        const SizedBox(height: 12),
                        Text(
                          'CRBCL Field Operations',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontFamily: CrbclTokens.fontHeading,
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: colorScheme.onSurface,
                            letterSpacing: 0.2,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Cote First Nation Family Wellness',
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: 13,
                            color: colorScheme.onSurface.withValues(alpha: 0.65),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 20),

                  // Login / Unlock Card
                  Card(
                    elevation: isDark ? 0 : 3,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                      side: BorderSide(
                        color: isDark ? colorScheme.outlineVariant : CrbclTokens.lightBorder,
                        width: 1,
                      ),
                    ),
                    color: colorScheme.surfaceContainer,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 20.0),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          // Error Banner
                          if (_errorMessage != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: colorScheme.error.withValues(alpha: 0.12),
                                borderRadius: BorderRadius.circular(8),
                                border: Border(
                                  left: BorderSide(color: colorScheme.error, width: 4),
                                ),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Icon(Icons.error_outline, size: 18, color: colorScheme.error),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _errorMessage!,
                                      style: TextStyle(
                                        color: isDark ? CrbclTokens.statusErrorDark : CrbclTokens.statusError,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // Status Message Banner
                          if (_statusMessage != null) ...[
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: CrbclTokens.statusSuccess.withValues(alpha: 0.12),
                                borderRadius: BorderRadius.circular(8),
                                border: const Border(
                                  left: BorderSide(color: CrbclTokens.statusSuccess, width: 4),
                                ),
                              ),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const Icon(Icons.check_circle_outline, size: 18, color: CrbclTokens.statusSuccess),
                                  const SizedBox(width: 8),
                                  Expanded(
                                    child: Text(
                                      _statusMessage!,
                                      style: TextStyle(
                                        color: isDark ? CrbclTokens.statusSuccessDark : CrbclTokens.statusSuccess,
                                        fontSize: 13,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 16),
                          ],

                          // Segmented Mode Switcher (Quick PIN Access vs Work Email & Password)
                          if (!_isSettingUpPin) ...[
                            Container(
                              margin: const EdgeInsets.only(bottom: 18),
                              decoration: BoxDecoration(
                                color: isDark ? Colors.black26 : const Color(0xFFECE7E1),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: isDark ? Colors.white12 : const Color(0xFFDDD7CF),
                                ),
                              ),
                              padding: const EdgeInsets.all(4),
                              child: Row(
                                children: [
                                  Expanded(
                                    child: InkWell(
                                      borderRadius: BorderRadius.circular(9),
                                      onTap: () {
                                        setState(() {
                                          _isOnlineLoginMode = false;
                                          _errorMessage = null;
                                        });
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(vertical: 9),
                                        decoration: BoxDecoration(
                                          color: !_isOnlineLoginMode
                                              ? (isDark ? colorScheme.primary : Colors.white)
                                              : Colors.transparent,
                                          borderRadius: BorderRadius.circular(9),
                                          boxShadow: !_isOnlineLoginMode
                                              ? [
                                                  BoxShadow(
                                                    color: Colors.black.withValues(alpha: 0.08),
                                                    blurRadius: 4,
                                                    offset: const Offset(0, 2),
                                                  )
                                                ]
                                              : null,
                                        ),
                                        child: Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Icon(
                                              Icons.pin_outlined,
                                              size: 16,
                                              color: !_isOnlineLoginMode
                                                  ? (isDark ? colorScheme.onPrimary : colorScheme.primary)
                                                  : colorScheme.onSurface.withValues(alpha: 0.6),
                                            ),
                                            const SizedBox(width: 6),
                                            Text(
                                              'Quick PIN',
                                              style: TextStyle(
                                                fontSize: 13,
                                                fontWeight: FontWeight.bold,
                                                color: !_isOnlineLoginMode
                                                    ? (isDark ? colorScheme.onPrimary : colorScheme.primary)
                                                    : colorScheme.onSurface.withValues(alpha: 0.7),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ),
                                  const SizedBox(width: 4),
                                  Expanded(
                                    child: InkWell(
                                      borderRadius: BorderRadius.circular(9),
                                      onTap: () {
                                        setState(() {
                                          _isOnlineLoginMode = true;
                                          _errorMessage = null;
                                        });
                                      },
                                      child: Container(
                                        padding: const EdgeInsets.symmetric(vertical: 9),
                                        decoration: BoxDecoration(
                                          color: _isOnlineLoginMode
                                              ? (isDark ? colorScheme.primary : Colors.white)
                                              : Colors.transparent,
                                          borderRadius: BorderRadius.circular(9),
                                          boxShadow: _isOnlineLoginMode
                                              ? [
                                                  BoxShadow(
                                                    color: Colors.black.withValues(alpha: 0.08),
                                                    blurRadius: 4,
                                                    offset: const Offset(0, 2),
                                                  )
                                                ]
                                              : null,
                                        ),
                                        child: Row(
                                          mainAxisAlignment: MainAxisAlignment.center,
                                          children: [
                                            Icon(
                                              Icons.email_outlined,
                                              size: 16,
                                              color: _isOnlineLoginMode
                                                  ? (isDark ? colorScheme.onPrimary : colorScheme.primary)
                                                  : colorScheme.onSurface.withValues(alpha: 0.6),
                                            ),
                                            const SizedBox(width: 6),
                                            Text(
                                              'Work Email',
                                              style: TextStyle(
                                                fontSize: 13,
                                                fontWeight: FontWeight.bold,
                                                color: _isOnlineLoginMode
                                                    ? (isDark ? colorScheme.onPrimary : colorScheme.primary)
                                                    : colorScheme.onSurface.withValues(alpha: 0.7),
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],

                          // View Modes
                          if (_isSettingUpPin)
                            _buildPinSetupView()
                          else if (_isOnlineLoginMode)
                            _buildOnlineLoginView()
                          else
                            _buildPinUnlockView(),

                          const Divider(height: 28),

                          // Discrete IT Admin Portal Entry Point
                          OutlinedButton.icon(
                            onPressed: () => Navigator.pushNamed(context, '/admin-login'),
                            style: OutlinedButton.styleFrom(
                              foregroundColor: const Color(0xFF6B21A8),
                              side: BorderSide(color: const Color(0xFF6B21A8).withValues(alpha: 0.4)),
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                              padding: const EdgeInsets.symmetric(vertical: 11),
                            ),
                            icon: const Icon(Icons.admin_panel_settings, size: 18),
                            label: const Text(
                              'IT Admin Portal',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),

                  // Footer security badge
                  const SizedBox(height: 16),
                  Center(
                    child: Wrap(
                      alignment: WrapAlignment.center,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      spacing: 6,
                      children: [
                        Icon(
                          Icons.verified_user_outlined,
                          size: 14,
                          color: colorScheme.onSurface.withValues(alpha: 0.5),
                        ),
                        Text(
                          'Encrypted Offline-First Field Platform',
                          style: TextStyle(
                            fontSize: 11,
                            color: colorScheme.onSurface.withValues(alpha: 0.5),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildPinUnlockView() {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    final displayName = _activeUserName?.isNotEmpty == true ? _activeUserName! : 'Staff Member';
    final emailDisplay = _activeUserEmail?.isNotEmpty == true ? _activeUserEmail! : '';

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Quick Offline Access',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: colorScheme.onSurface,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 8),

        // User badge showing clearly which account is unlocking, or email input if not saved
        if (emailDisplay.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: isDark ? Colors.white10 : colorScheme.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: colorScheme.primary.withValues(alpha: 0.2)),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 14,
                  backgroundColor: colorScheme.primary.withValues(alpha: 0.2),
                  child: Icon(Icons.person, size: 16, color: colorScheme.primary),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        displayName,
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        emailDisplay,
                        style: TextStyle(
                          fontSize: 11,
                          color: colorScheme.onSurface.withValues(alpha: 0.7),
                        ),
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
        ] else ...[
          TextField(
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            decoration: const InputDecoration(
              labelText: 'Staff Work Email',
              hintText: 'you@crbcl.ca',
              prefixIcon: Icon(Icons.email_outlined),
              border: OutlineInputBorder(),
              isDense: true,
            ),
          ),
          const SizedBox(height: 12),
        ],

        Text(
          'Enter your personal 6-digit Quick PIN',
          style: TextStyle(
            fontSize: 12,
            color: colorScheme.onSurface.withValues(alpha: 0.65),
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _pinController,
          keyboardType: TextInputType.number,
          obscureText: _obscurePin,
          maxLength: 6,
          decoration: InputDecoration(
            labelText: 'Enter 6-digit PIN',
            prefixIcon: const Icon(Icons.lock_outline),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePin ? Icons.visibility_off : Icons.visibility,
                semanticLabel: _obscurePin ? 'Show PIN' : 'Hide PIN',
              ),
              onPressed: () {
                setState(() => _obscurePin = !_obscurePin);
              },
            ),
            border: const OutlineInputBorder(),
          ),
          onSubmitted: (_) => _handlePinUnlock(),
        ),
        const SizedBox(height: 12),

        ElevatedButton(
          onPressed: _handlePinUnlock,
          style: ElevatedButton.styleFrom(
            backgroundColor: colorScheme.primary,
            foregroundColor: colorScheme.onPrimary,
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.lock_open, size: 18),
              const SizedBox(width: 8),
              Text(
                emailDisplay.isNotEmpty ? 'Unlock Vault' : 'Sign In with PIN',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
            ],
          ),
        ),
        const SizedBox(height: 14),

        // Switch Option
        if (emailDisplay.isNotEmpty)
          OutlinedButton.icon(
            onPressed: _handleSwitchUser,
            icon: const Icon(Icons.swap_horiz, size: 18),
            label: const Text('Switch Account / Sign In with Credentials'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          )
        else
          OutlinedButton.icon(
            onPressed: () {
              setState(() {
                _isOnlineLoginMode = true;
                _errorMessage = null;
              });
            },
            icon: const Icon(Icons.password, size: 18),
            label: const Text('Use Email & Password instead'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 12),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
      ],
    );
  }

  Widget _buildOnlineLoginView() {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;
    final isDark = theme.brightness == Brightness.dark;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'CRBCL Staff Sign In',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: colorScheme.onSurface,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 4),
        Text(
          'Log in to your account',
          style: TextStyle(
            fontSize: 13,
            color: colorScheme.onSurface.withValues(alpha: 0.65),
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 18),

        // Continue with Google Button matching web
        OutlinedButton(
          onPressed: _handleGoogleAuth,
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            side: BorderSide(color: isDark ? Colors.white24 : const Color(0xFFE8E3DF)),
            backgroundColor: isDark ? colorScheme.surface : Colors.white,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: const [
              GoogleIcon(size: 18),
              SizedBox(width: 8),
              Flexible(
                child: Text(
                  'Continue with Google',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // OR Divider
        Row(
          children: [
            Expanded(child: Divider(color: isDark ? Colors.white24 : const Color(0xFFE8E3DF))),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12),
              child: Text(
                'OR',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: colorScheme.onSurface.withValues(alpha: 0.5),
                ),
              ),
            ),
            Expanded(child: Divider(color: isDark ? Colors.white24 : const Color(0xFFE8E3DF))),
          ],
        ),
        const SizedBox(height: 16),

        // Work Email
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(
            labelText: 'Staff Work Email',
            hintText: 'you@crbcl.ca',
            prefixIcon: Icon(Icons.email_outlined),
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 14),

        // Password
        TextField(
          controller: _passwordController,
          obscureText: _obscurePassword,
          decoration: InputDecoration(
            labelText: 'Password',
            hintText: '••••••••',
            prefixIcon: const Icon(Icons.key_outlined),
            suffixIcon: IconButton(
              icon: Icon(
                _obscurePassword ? Icons.visibility_off : Icons.visibility,
                semanticLabel: _obscurePassword ? 'Show password' : 'Hide password',
              ),
              onPressed: () {
                setState(() => _obscurePassword = !_obscurePassword);
              },
            ),
            border: const OutlineInputBorder(),
          ),
          onSubmitted: (_) => _handleOnlineLogin(),
        ),
        const SizedBox(height: 6),

        // Forgot Password link
        Align(
          alignment: Alignment.centerRight,
          child: TextButton(
            onPressed: () => Navigator.pushNamed(context, '/forgot-password'),
            style: TextButton.styleFrom(visualDensity: VisualDensity.compact),
            child: const Text('Forgot password?'),
          ),
        ),
        const SizedBox(height: 8),

        // Login Button
        ElevatedButton(
          onPressed: _handleOnlineLogin,
          style: ElevatedButton.styleFrom(
            backgroundColor: colorScheme.primary,
            foregroundColor: colorScheme.onPrimary,
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 8),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            mainAxisSize: MainAxisSize.min,
            children: const [
              Icon(Icons.login, size: 18),
              SizedBox(width: 8),
              Flexible(
                child: Text(
                  'Authenticate & Register Device',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 1,
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),

        // Quick PIN button
        OutlinedButton.icon(
          onPressed: () {
            setState(() {
              _isOnlineLoginMode = false;
              _errorMessage = null;
            });
          },
          icon: const Icon(Icons.pin_outlined, size: 18),
          label: const Text('Quick Sign In with 6-Digit PIN'),
          style: OutlinedButton.styleFrom(
            padding: const EdgeInsets.symmetric(vertical: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
        ),
        const SizedBox(height: 16),

        // Sign Up link matching web
        Wrap(
          alignment: WrapAlignment.center,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            Text(
              "Don't have an account? ",
              style: TextStyle(
                fontSize: 13,
                color: colorScheme.onSurface.withValues(alpha: 0.7),
              ),
            ),
            GestureDetector(
              onTap: () => Navigator.pushNamed(context, '/signup'),
              child: Text(
                'Sign Up',
                style: TextStyle(
                  fontSize: 13,
                  fontWeight: FontWeight.bold,
                  color: colorScheme.primary,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Switch back to Quick PIN Access if user has credentials saved
        FutureBuilder<bool>(
          future: _authService.hasSavedCredentials(email: _activeUserEmail),
          builder: (context, snapshot) {
            if (snapshot.data == true) {
              return TextButton(
                onPressed: () {
                  setState(() {
                    _isOnlineLoginMode = false;
                    _errorMessage = null;
                  });
                },
                child: const Text('Switch back to Quick PIN Access'),
              );
            }
            return const SizedBox.shrink();
          },
        ),
      ],
    );
  }

  Widget _buildPinSetupView() {
    final theme = Theme.of(context);
    final colorScheme = theme.colorScheme;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Text(
          'Set Quick Access PIN',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: colorScheme.onSurface,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 6),
        Text(
          'Create a 6-digit personal PIN for offline unlocking in the field.',
          style: TextStyle(
            fontSize: 12,
            color: colorScheme.onSurface.withValues(alpha: 0.65),
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 16),

        TextField(
          controller: _newPinController,
          keyboardType: TextInputType.number,
          obscureText: _obscureNewPin,
          maxLength: 6,
          decoration: InputDecoration(
            labelText: 'New 6-digit PIN',
            prefixIcon: const Icon(Icons.pin),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureNewPin ? Icons.visibility_off : Icons.visibility,
                semanticLabel: _obscureNewPin ? 'Show PIN' : 'Hide PIN',
              ),
              onPressed: () {
                setState(() => _obscureNewPin = !_obscureNewPin);
              },
            ),
            border: const OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 12),

        TextField(
          controller: _confirmPinController,
          keyboardType: TextInputType.number,
          obscureText: _obscureConfirmPin,
          maxLength: 6,
          decoration: InputDecoration(
            labelText: 'Confirm 6-digit PIN',
            prefixIcon: const Icon(Icons.check_circle_outline),
            suffixIcon: IconButton(
              icon: Icon(
                _obscureConfirmPin ? Icons.visibility_off : Icons.visibility,
                semanticLabel: _obscureConfirmPin ? 'Show PIN' : 'Hide PIN',
              ),
              onPressed: () {
                setState(() => _obscureConfirmPin = !_obscureConfirmPin);
              },
            ),
            border: const OutlineInputBorder(),
          ),
          onSubmitted: (_) => _handleSetPin(),
        ),
        const SizedBox(height: 16),

        ElevatedButton(
          onPressed: _handleSetPin,
          style: ElevatedButton.styleFrom(
            backgroundColor: colorScheme.primary,
            foregroundColor: colorScheme.onPrimary,
            padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 12),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: const [
              Icon(Icons.save, size: 18),
              SizedBox(width: 8),
              Text('Save PIN & Enter App', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            ],
          ),
        ),
      ],
    );
  }
}
