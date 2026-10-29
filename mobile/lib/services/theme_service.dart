import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:http/http.dart' as http;

/// Authoritative palette tokens derived from the CRBCL production web application
/// (`src/index.css` and `src/theme/`).
class CrbclPalette {
  final String key;
  final String label;
  final Color primary;
  final Color darkPrimary;
  final Color? onPrimary;

  const CrbclPalette({
    required this.key,
    required this.label,
    required this.primary,
    required this.darkPrimary,
    this.onPrimary,
  });
}

/// Official brand and design tokens for the CRBCL mobile application.
/// Strictly aligned with the CRBCL web platform tokens.
class CrbclTokens {
  // Web Core Brand Colors
  static const Color crbclCrimson = Color(0xFF9B2F27);      // Light primary (--primary: 4 60% 38%)
  static const Color crbclCrimsonDark = Color(0xFFC64339);  // Dark primary (.dark --primary: 4 55% 50%)
  static const Color crbclGold = Color(0xFFDA962F);         // Web accent gold (--accent: 36 68% 52%)

  // Light Mode Surfaces & Text (from src/index.css)
  static const Color lightBackground = Color(0xFFFBFAF9);   // --background: 30 20% 98%
  static const Color lightForeground = Color(0xFF1F1814);   // --foreground: 20 20% 10%
  static const Color lightCard = Color(0xFFFDFCFC);         // --card: 0 10% 99%
  static const Color lightSecondary = Color(0xFFF4F0EB);    // --secondary: 30 20% 94%
  static const Color lightMuted = Color(0xFFF2F0ED);        // --muted: 30 10% 94%
  static const Color lightMutedForeground = Color(0xFF6B5D55); // High-contrast accessible muted
  static const Color lightBorder = Color(0xFFE7E3DF);       // --border: 30 12% 89%
  static const Color lightBorderStrong = Color(0xFFD3CCC5);

  // Dark Mode Surfaces & Text (from src/index.css .dark)
  static const Color darkBackground = Color(0xFF15110E);    // .dark --background: 20 20% 7%
  static const Color darkForeground = Color(0xFFF0EDEA);    // .dark --foreground: 30 10% 93%
  static const Color darkCard = Color(0xFF1E1815);          // .dark --card: 20 18% 10%
  static const Color darkSecondary = Color(0xFF2F2723);     // .dark --secondary: 20 15% 16%
  static const Color darkMuted = Color(0xFF2E2724);         // .dark --muted: 20 12% 16%
  static const Color darkMutedForeground = Color(0xFF9E9287); // High-contrast accessible muted
  static const Color darkBorder = Color(0xFF332C28);        // .dark --border: 20 12% 18%
  static const Color darkBorderStrong = Color(0xFF473E39);

  // Status Colors (Consistent across modes with theme-adapted badges)
  static const Color statusSuccess = Color(0xFF31815C);     // Web success green
  static const Color statusSuccessDark = Color(0xFF3B9B6E);
  static const Color statusWarning = Color(0xFFD97706);     // Web warning amber
  static const Color statusWarningDark = Color(0xFFF4A125);
  static const Color statusError = Color(0xFFDC2828);       // Web destructive red
  static const Color statusErrorDark = Color(0xFFE04848);
  static const Color statusInfo = Color(0xFF2563EB);        // Web info blue
  static const Color statusInfoDark = Color(0xFF60A5FA);
  static const Color statusReview = Color(0xFF843FA6);      // Web review purple
  static const Color statusReviewDark = Color(0xFF9D59C0);

  // Fonts
  static const String fontBody = 'Inter';
  static const String fontHeading = 'PlayfairDisplay';
}

class MobileThemeService extends ChangeNotifier {
  static const _storageKey = 'crbcl_mobile_theme_prefs';
  static const _secureStorage = FlutterSecureStorage();

  /// 14 Official Accent Palettes matching the web application (`src/index.css` & theme tokens)
  static const List<CrbclPalette> palettes = [
    CrbclPalette(
      key: 'crbcl',
      label: 'CRBCL Crimson (Default)',
      primary: Color(0xFF9B2F27),
      darkPrimary: Color(0xFFC64339),
    ),
    CrbclPalette(
      key: 'burgundy',
      label: 'Deep Burgundy',
      primary: Color(0xFF832134),
      darkPrimary: Color(0xFFB82E49),
    ),
    CrbclPalette(
      key: 'earth',
      label: 'Warm Earth & Clay',
      primary: Color(0xFFA05422),
      darkPrimary: Color(0xFFCA6A2B),
    ),
    CrbclPalette(
      key: 'forest',
      label: 'Evergreen & Sage',
      primary: Color(0xFF267346),
      darkPrimary: Color(0xFF36A162),
    ),
    CrbclPalette(
      key: 'prairie',
      label: 'Prairie Sun & Gold',
      primary: Color(0xFFA56F12),
      darkPrimary: Color(0xFFDC9518),
    ),
    CrbclPalette(
      key: 'ocean',
      label: 'Deep River Blue',
      primary: Color(0xFF245BA8),
      darkPrimary: Color(0xFF2D72D2),
    ),
    CrbclPalette(
      key: 'teal',
      label: 'Boreal Spruce Teal',
      primary: Color(0xFF218379),
      darkPrimary: Color(0xFF2BAB9F),
    ),
    CrbclPalette(
      key: 'neutral',
      label: 'Refined Slate',
      primary: Color(0xFF47536B),
      darkPrimary: Color(0xFF5C6B8A),
    ),
    CrbclPalette(
      key: 'pink',
      label: 'Pink',
      primary: Color(0xFFD11A66),
      darkPrimary: Color(0xFFE02975),
    ),
    CrbclPalette(
      key: 'light-pink',
      label: 'Light Pink',
      primary: Color(0xFFD93A6F),
      darkPrimary: Color(0xFFDE5482),
    ),
    CrbclPalette(
      key: 'purple',
      label: 'Purple',
      primary: Color(0xFF7622A0),
      darkPrimary: Color(0xFF952BCA),
    ),
    CrbclPalette(
      key: 'light-purple',
      label: 'Light Purple',
      primary: Color(0xFF6F37BE),
      darkPrimary: Color(0xFF8551CD),
    ),
    CrbclPalette(
      key: 'sky-blue',
      label: 'Sky Blue',
      primary: Color(0xFF0C80B6),
      darkPrimary: Color(0xFF0E9BDD),
    ),
    CrbclPalette(
      key: 'yellow',
      label: 'Yellow',
      primary: Color(0xFFEAB308),
      darkPrimary: Color(0xFFFBBF24),
      onPrimary: Colors.black,
    ),
  ];

  ThemeMode _themeMode = ThemeMode.system;
  String _accentKey = 'crbcl';
  String _density = 'comfortable';
  bool _highContrast = false;
  bool _reducedMotion = false;
  String? _defaultLandingDashboard;

  ThemeMode get themeMode => _themeMode;
  String get accentKey => _accentKey;
  String get density => _density;
  bool get highContrast => _highContrast;
  bool get reducedMotion => _reducedMotion;
  String? get defaultLandingDashboard => _defaultLandingDashboard;

  CrbclPalette get activePalette {
    return palettes.firstWhere(
      (p) => p.key == _accentKey,
      orElse: () => palettes.first,
    );
  }

  MobileThemeService() {
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    try {
      final raw = await _secureStorage.read(key: _storageKey);
      if (raw != null) {
        final data = json.decode(raw);
        _applyParsedData(data);
        notifyListeners();
      }
    } catch (_) {
      // Use defaults if storage read fails
    }
  }

  void _applyParsedData(Map<String, dynamic> data) {
    if (data.containsKey('theme_mode')) {
      final modeStr = data['theme_mode'] as String?;
      if (modeStr == 'light') {
        _themeMode = ThemeMode.light;
      } else if (modeStr == 'dark') {
        _themeMode = ThemeMode.dark;
      } else {
        _themeMode = ThemeMode.system;
      }
    }
    if (data.containsKey('accent_theme')) {
      final raw = data['accent_theme'] as String?;
      final accent = raw?.replaceAll('_', '-');
      if (accent != null && palettes.any((p) => p.key == accent)) {
        _accentKey = accent;
      }
    }
    if (data.containsKey('density')) {
      _density = data['density'] == 'compact' ? 'compact' : 'comfortable';
    }
    if (data.containsKey('high_contrast')) {
      _highContrast = data['high_contrast'] == true;
    }
    if (data.containsKey('reduced_motion')) {
      _reducedMotion = data['reduced_motion'] == true;
    }
    if (data.containsKey('default_landing_dashboard')) {
      _defaultLandingDashboard = data['default_landing_dashboard'] as String?;
    }
  }

  Future<void> updatePreferences({
    ThemeMode? mode,
    String? accent,
    String? density,
    bool? highContrast,
    bool? reducedMotion,
    String? defaultLanding,
    String? authToken,
    String? backendUrl,
  }) async {
    if (mode != null) _themeMode = mode;
    if (accent != null) {
      final normalizedAccent = accent.replaceAll('_', '-');
      if (palettes.any((p) => p.key == normalizedAccent)) {
        _accentKey = normalizedAccent;
      }
    }
    if (density != null) _density = density;
    if (highContrast != null) _highContrast = highContrast;
    if (reducedMotion != null) _reducedMotion = reducedMotion;
    if (defaultLanding != null) _defaultLandingDashboard = defaultLanding;

    final jsonMap = {
      'theme_mode': _themeMode == ThemeMode.light
          ? 'light'
          : _themeMode == ThemeMode.dark
              ? 'dark'
              : 'system',
      'accent_theme': _accentKey,
      'density': _density,
      'high_contrast': _highContrast,
      'reduced_motion': _reducedMotion,
      'default_landing_dashboard': _defaultLandingDashboard,
    };

    await _secureStorage.write(key: _storageKey, value: json.encode(jsonMap));
    notifyListeners();

    // Sync to backend if token provided
    if (authToken != null && backendUrl != null) {
      try {
        final uri = Uri.parse('$backendUrl/api/v1/users/me/preferences');
        await http.put(
          uri,
          headers: {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer $authToken',
          },
          body: json.encode({'appearance': jsonMap}),
        );
      } catch (_) {
        // Safe offline fallback
      }
    }
  }

  Future<void> syncWithBackend(String authToken, String backendUrl) async {
    try {
      final uri = Uri.parse('$backendUrl/api/v1/users/me/preferences');
      final res = await http.get(
        uri,
        headers: {'Authorization': 'Bearer $authToken'},
      );
      if (res.statusCode == 200) {
        final body = json.decode(res.body);
        if (body is Map<String, dynamic> && body.containsKey('appearance')) {
          _applyParsedData(body['appearance'] as Map<String, dynamic>);
          await _secureStorage.write(
            key: _storageKey,
            value: json.encode(body['appearance']),
          );
          notifyListeners();
        }
      }
    } catch (_) {
      // Offline fallback: retain local cached preferences
    }
  }

  ThemeData getLightTheme() {
    final palette = activePalette;
    final primaryColor = palette.primary;
    final onPrimaryColor = palette.onPrimary ?? Colors.white;

    final colorScheme = ColorScheme.light(
      primary: primaryColor,
      onPrimary: onPrimaryColor,
      primaryContainer: const Color(0xFFF6E8E6),
      onPrimaryContainer: const Color(0xFF5A1612),
      secondary: CrbclTokens.lightSecondary,
      onSecondary: CrbclTokens.lightForeground,
      secondaryContainer: const Color(0xFFEBE5DE),
      onSecondaryContainer: CrbclTokens.lightForeground,
      tertiary: CrbclTokens.crbclGold,
      onTertiary: Colors.black,
      error: CrbclTokens.statusError,
      onError: Colors.white,
      surface: _highContrast ? Colors.white : CrbclTokens.lightBackground,
      onSurface: CrbclTokens.lightForeground,
      surfaceContainerLowest: Colors.white,
      surfaceContainerLow: CrbclTokens.lightBackground,
      surfaceContainer: CrbclTokens.lightCard,
      surfaceContainerHigh: CrbclTokens.lightSecondary,
      surfaceContainerHighest: CrbclTokens.lightMuted,
      outline: _highContrast ? Colors.black87 : CrbclTokens.lightBorderStrong,
      outlineVariant: CrbclTokens.lightBorder,
    );

    final cardBorder = _highContrast
        ? const BorderSide(color: Colors.black87, width: 1.5)
        : BorderSide(color: CrbclTokens.lightBorder, width: 1);

    return ThemeData(
      useMaterial3: true,
      fontFamily: CrbclTokens.fontBody,
      brightness: Brightness.light,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: colorScheme.surface,
      dividerColor: CrbclTokens.lightBorder,
      appBarTheme: AppBarTheme(
        backgroundColor: primaryColor,
        foregroundColor: onPrimaryColor,
        elevation: _highContrast ? 2 : 0,
        centerTitle: false,
        titleTextStyle: const TextStyle(
          fontFamily: CrbclTokens.fontBody,
          fontWeight: FontWeight.w600,
          fontSize: 18,
          color: Colors.white,
        ),
      ),
      cardTheme: CardThemeData(
        color: CrbclTokens.lightCard,
        elevation: _highContrast ? 2 : 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 12),
          side: cardBorder,
        ),
        margin: EdgeInsets.symmetric(vertical: _density == 'compact' ? 4 : 6),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: onPrimaryColor,
          elevation: _highContrast ? 2 : 0,
          padding: EdgeInsets.symmetric(
            horizontal: 18,
            vertical: _density == 'compact' ? 10 : 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 10),
          ),
          textStyle: const TextStyle(
            fontFamily: CrbclTokens.fontBody,
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          side: BorderSide(color: primaryColor, width: _highContrast ? 1.5 : 1.0),
          padding: EdgeInsets.symmetric(
            horizontal: 16,
            vertical: _density == 'compact' ? 10 : 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 10),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: Colors.white,
        contentPadding: EdgeInsets.symmetric(
          horizontal: 14,
          vertical: _density == 'compact' ? 10 : 14,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: CrbclTokens.lightBorderStrong),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(
            color: _highContrast ? Colors.black87 : CrbclTokens.lightBorderStrong,
            width: _highContrast ? 1.5 : 1.0,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: primaryColor, width: 2.0),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: CrbclTokens.statusError, width: 1.5),
        ),
        labelStyle: const TextStyle(color: CrbclTokens.lightMutedForeground, fontSize: 14),
        hintStyle: const TextStyle(color: CrbclTokens.lightMutedForeground, fontSize: 14),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: Colors.white,
        selectedItemColor: primaryColor,
        unselectedItemColor: CrbclTokens.lightMutedForeground,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 11),
        unselectedLabelStyle: const TextStyle(fontSize: 11),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      drawerTheme: DrawerThemeData(
        backgroundColor: CrbclTokens.lightCard,
        elevation: 4,
      ),
    );
  }

  ThemeData getDarkTheme() {
    final palette = activePalette;
    final primaryColor = palette.darkPrimary;
    const onPrimaryColor = Colors.white;

    final colorScheme = ColorScheme.dark(
      primary: primaryColor,
      onPrimary: onPrimaryColor,
      primaryContainer: const Color(0xFF401613),
      onPrimaryContainer: const Color(0xFFF7CECA),
      secondary: CrbclTokens.darkSecondary,
      onSecondary: CrbclTokens.darkForeground,
      secondaryContainer: const Color(0xFF382E28),
      onSecondaryContainer: CrbclTokens.darkForeground,
      tertiary: CrbclTokens.crbclGold,
      onTertiary: Colors.black,
      error: CrbclTokens.statusErrorDark,
      onError: Colors.white,
      surface: _highContrast ? Colors.black : CrbclTokens.darkBackground,
      onSurface: CrbclTokens.darkForeground,
      surfaceContainerLowest: const Color(0xFF0F0B09),
      surfaceContainerLow: CrbclTokens.darkBackground,
      surfaceContainer: CrbclTokens.darkCard,
      surfaceContainerHigh: CrbclTokens.darkSecondary,
      surfaceContainerHighest: CrbclTokens.darkMuted,
      outline: _highContrast ? Colors.white70 : CrbclTokens.darkBorderStrong,
      outlineVariant: CrbclTokens.darkBorder,
    );

    final cardBorder = _highContrast
        ? const BorderSide(color: Colors.white70, width: 1.5)
        : BorderSide(color: CrbclTokens.darkBorder, width: 1);

    return ThemeData(
      useMaterial3: true,
      fontFamily: CrbclTokens.fontBody,
      brightness: Brightness.dark,
      colorScheme: colorScheme,
      scaffoldBackgroundColor: colorScheme.surface,
      dividerColor: CrbclTokens.darkBorder,
      appBarTheme: AppBarTheme(
        backgroundColor: const Color(0xFF1B1512),
        foregroundColor: CrbclTokens.darkForeground,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: const TextStyle(
          fontFamily: CrbclTokens.fontBody,
          fontWeight: FontWeight.w600,
          fontSize: 18,
          color: CrbclTokens.darkForeground,
        ),
      ),
      cardTheme: CardThemeData(
        color: CrbclTokens.darkCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 12),
          side: cardBorder,
        ),
        margin: EdgeInsets.symmetric(vertical: _density == 'compact' ? 4 : 6),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          backgroundColor: primaryColor,
          foregroundColor: onPrimaryColor,
          elevation: 0,
          padding: EdgeInsets.symmetric(
            horizontal: 18,
            vertical: _density == 'compact' ? 10 : 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 10),
          ),
          textStyle: const TextStyle(
            fontFamily: CrbclTokens.fontBody,
            fontWeight: FontWeight.w600,
            fontSize: 14,
          ),
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          foregroundColor: primaryColor,
          side: BorderSide(color: primaryColor, width: _highContrast ? 1.5 : 1.0),
          padding: EdgeInsets.symmetric(
            horizontal: 16,
            vertical: _density == 'compact' ? 10 : 14,
          ),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(_density == 'compact' ? 8 : 10),
          ),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          foregroundColor: primaryColor,
          textStyle: const TextStyle(fontWeight: FontWeight.w600),
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: CrbclTokens.darkCard,
        contentPadding: EdgeInsets.symmetric(
          horizontal: 14,
          vertical: _density == 'compact' ? 10 : 14,
        ),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: CrbclTokens.darkBorderStrong),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(
            color: _highContrast ? Colors.white70 : CrbclTokens.darkBorderStrong,
            width: _highContrast ? 1.5 : 1.0,
          ),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: BorderSide(color: primaryColor, width: 2.0),
        ),
        errorBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: CrbclTokens.statusErrorDark, width: 1.5),
        ),
        labelStyle: const TextStyle(color: CrbclTokens.darkMutedForeground, fontSize: 14),
        hintStyle: const TextStyle(color: CrbclTokens.darkMutedForeground, fontSize: 14),
      ),
      bottomNavigationBarTheme: BottomNavigationBarThemeData(
        backgroundColor: const Color(0xFF1B1512),
        selectedItemColor: primaryColor,
        unselectedItemColor: CrbclTokens.darkMutedForeground,
        selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 11),
        unselectedLabelStyle: const TextStyle(fontSize: 11),
        type: BottomNavigationBarType.fixed,
        elevation: 8,
      ),
      drawerTheme: const DrawerThemeData(
        backgroundColor: Color(0xFF1B1512),
        elevation: 4,
      ),
    );
  }
}
