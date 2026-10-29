import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { api } from '@/api';

const THEME_STORAGE_KEY = 'crbcl_theme_preferences';

export const VALID_ACCENTS = [
  { key: 'crbcl', label: 'CRBCL Crimson (Default)', color: '#8B2626', bgHsl: '4 60% 38%', darkHsl: '4 55% 50%', sidebarHsl: '4 60% 50%', fgHsl: '0 0% 100%' },
  { key: 'burgundy', label: 'Deep Burgundy', color: '#821D30', bgHsl: '348 60% 32%', darkHsl: '348 55% 48%', sidebarHsl: '348 60% 45%', fgHsl: '0 0% 100%' },
  { key: 'earth', label: 'Warm Earth & Clay', color: '#9E4A22', bgHsl: '24 65% 38%', darkHsl: '24 60% 50%', sidebarHsl: '24 65% 48%', fgHsl: '0 0% 100%' },
  { key: 'forest', label: 'Evergreen & Sage', color: '#267344', bgHsl: '145 50% 30%', darkHsl: '145 45% 44%', sidebarHsl: '145 50% 42%', fgHsl: '0 0% 100%' },
  { key: 'prairie', label: 'Prairie Sun & Gold', color: '#A57313', bgHsl: '38 80% 36%', darkHsl: '38 75% 48%', sidebarHsl: '38 80% 48%', fgHsl: '0 0% 100%' },
  { key: 'ocean', label: 'Deep River Blue', color: '#245C99', bgHsl: '215 65% 40%', darkHsl: '215 60% 52%', sidebarHsl: '215 65% 50%', fgHsl: '0 0% 100%' },
  { key: 'teal', label: 'Boreal Spruce Teal', color: '#217A6C', bgHsl: '174 60% 32%', darkHsl: '174 55% 44%', sidebarHsl: '174 60% 42%', fgHsl: '0 0% 100%' },
  { key: 'neutral', label: 'Refined Slate', color: '#485669', bgHsl: '220 20% 35%', darkHsl: '220 18% 52%', sidebarHsl: '220 20% 45%', fgHsl: '0 0% 100%' },
  { key: 'pink', label: 'Pink', color: '#D81B60', bgHsl: '335 78% 46%', darkHsl: '335 75% 58%', sidebarHsl: '335 75% 52%', fgHsl: '0 0% 100%' },
  { key: 'light-pink', label: 'Light Pink', color: '#E57399', bgHsl: '340 68% 54%', darkHsl: '340 75% 68%', sidebarHsl: '340 68% 60%', fgHsl: '0 0% 100%' },
  { key: 'purple', label: 'Purple', color: '#7B1FA2', bgHsl: '280 65% 38%', darkHsl: '280 60% 56%', sidebarHsl: '280 65% 48%', fgHsl: '0 0% 100%' },
  { key: 'light-purple', label: 'Light Purple', color: '#9575CD', bgHsl: '265 55% 48%', darkHsl: '265 65% 66%', sidebarHsl: '265 55% 56%', fgHsl: '0 0% 100%' },
  { key: 'sky-blue', label: 'Sky Blue', color: '#0284C7', bgHsl: '199 88% 38%', darkHsl: '199 80% 52%', sidebarHsl: '199 88% 46%', fgHsl: '0 0% 100%' },
  { key: 'yellow', label: 'Yellow', color: '#EAB308', bgHsl: '45 96% 45%', darkHsl: '45 95% 52%', sidebarHsl: '45 96% 45%', fgHsl: '20 20% 10%' },
];

export const DEFAULT_PREFERENCES = {
  theme_mode: 'system', // 'light' | 'dark' | 'system'
  accent_theme: 'crbcl',
  density: 'comfortable', // 'comfortable' | 'compact'
  sidebar_collapsed: false,
  card_radius: 'rounded', // 'rounded' | 'subtle'
  reduced_motion: false,
  high_contrast: false,
  default_landing_dashboard: null,
};

function getStoredPreferences() {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      return { ...DEFAULT_PREFERENCES, ...parsed };
    }
  } catch (e) {
    console.warn('Failed to parse stored theme preferences:', e);
  }
  return { ...DEFAULT_PREFERENCES };
}

const ThemeContext = createContext(null);

export function ThemeProvider({ children }) {
  const [preferences, setPreferences] = useState(getStoredPreferences);
  const [systemIsDark, setSystemIsDark] = useState(() => {
    return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  });
  const [isSyncing, setIsSyncing] = useState(false);

  // Monitor system dark mode changes
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handler = (e) => setSystemIsDark(e.matches);
    mediaQuery.addEventListener('change', handler);
    return () => mediaQuery.removeEventListener('change', handler);
  }, []);

  // Compute active dark mode state
  const isDark = preferences.theme_mode === 'dark' || (preferences.theme_mode === 'system' && systemIsDark);

  // Apply DOM classes and inline CSS properties immediately whenever preferences or system dark changes
  useEffect(() => {
    const root = document.documentElement;

    // Preserve original white branding on login and authentication pages
    const pathname = typeof window !== 'undefined' ? (window.location.pathname || '') : '';
    const isAuthRoute = ['/login', '/admin/login', '/register', '/forgot-password', '/reset-password'].some(
      (p) => pathname === p || pathname.startsWith(p + '/')
    );

    if (isAuthRoute) {
      root.classList.remove('dark');
      VALID_ACCENTS.forEach(({ key }) => {
        root.classList.remove(`theme-${key}`);
        if (key.includes('-')) {
          root.classList.remove(`theme-${key.replace('-', '_')}`);
        }
      });
      root.classList.add('theme-crbcl');
      root.style.removeProperty('--primary');
      root.style.removeProperty('--ring');
      root.style.removeProperty('--sidebar-primary');
      root.style.removeProperty('--sidebar-ring');
      root.style.removeProperty('--primary-foreground');
      root.style.removeProperty('--sidebar-primary-foreground');
      return;
    }

    // Dark mode
    if (isDark) {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }

    // Accent theme classes
    VALID_ACCENTS.forEach(({ key }) => {
      root.classList.remove(`theme-${key}`);
      if (key.includes('-')) {
        root.classList.remove(`theme-${key.replace('-', '_')}`);
      }
    });
    const currentAccent = preferences.accent_theme ? preferences.accent_theme.replace('_', '-') : 'crbcl';
    const activeAccent = VALID_ACCENTS.find((a) => a.key === currentAccent) || VALID_ACCENTS[0];
    const validKey = activeAccent.key;
    root.classList.add(`theme-${validKey}`);

    // Apply inline CSS variables to guarantee instant, unpurgeable theme styling across all components
    const primaryHsl = isDark ? (activeAccent.darkHsl || activeAccent.bgHsl) : activeAccent.bgHsl;
    const sidebarPrimaryHsl = isDark ? (activeAccent.darkSidebarHsl || activeAccent.sidebarHsl || activeAccent.bgHsl) : (activeAccent.sidebarHsl || activeAccent.bgHsl);
    const fgHsl = activeAccent.fgHsl || '0 0% 100%';

    root.style.setProperty('--primary', primaryHsl);
    root.style.setProperty('--ring', primaryHsl);
    root.style.setProperty('--sidebar-primary', sidebarPrimaryHsl);
    root.style.setProperty('--sidebar-ring', sidebarPrimaryHsl);
    root.style.setProperty('--primary-foreground', fgHsl);
    root.style.setProperty('--sidebar-primary-foreground', fgHsl);

    // Density
    if (preferences.density === 'compact') {
      root.classList.add('density-compact');
    } else {
      root.classList.remove('density-compact');
    }

    // Radius
    root.classList.remove('radius-rounded', 'radius-subtle');
    root.classList.add(`radius-${preferences.card_radius === 'subtle' ? 'subtle' : 'rounded'}`);

    // High contrast
    if (preferences.high_contrast) {
      root.classList.add('high-contrast');
    } else {
      root.classList.remove('high-contrast');
    }

    // Reduced motion
    if (preferences.reduced_motion) {
      root.classList.add('reduced-motion');
    } else {
      root.classList.remove('reduced-motion');
    }

    // Persist to local storage
    try {
      localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(preferences));
    } catch (e) {
      console.warn('Failed to save theme preferences to localStorage:', e);
    }
  }, [preferences, isDark]);

  // Pull server-authoritative preferences on mount or auth refresh
  const syncWithServer = useCallback(async () => {
    try {
      const res = await api.get('/api/v1/users/me/preferences');
      if (res && res.appearance) {
        setPreferences((prev) => ({
          ...prev,
          ...res.appearance,
        }));
      }
    } catch {
      // Not authenticated or offline, local preferences remain active
    }
  }, []);

  useEffect(() => {
    syncWithServer();
  }, [syncWithServer]);

  // Update preferences with immediate local application and backend persistence
  const updatePreferences = useCallback(async (partial) => {
    let updated;
    setPreferences((prev) => {
      updated = { ...prev, ...partial };
      return updated;
    });

    setIsSyncing(true);
    try {
      await api.put('/api/v1/users/me/preferences', {
        appearance: {
          theme_mode: updated.theme_mode,
          accent_theme: updated.accent_theme,
          density: updated.density,
          sidebar_collapsed: updated.sidebar_collapsed,
          card_radius: updated.card_radius,
          reduced_motion: updated.reduced_motion,
          high_contrast: updated.high_contrast,
          default_landing_dashboard: updated.default_landing_dashboard || null,
        },
      });
      return { success: true };
    } catch (err) {
      console.warn('Failed to persist preferences to server:', err);
      return { success: false, error: err };
    } finally {
      setIsSyncing(false);
    }
  }, []);

  // Reset to CRBCL Defaults
  const resetToDefaults = useCallback(async () => {
    return await updatePreferences(DEFAULT_PREFERENCES);
  }, [updatePreferences]);

  const value = {
    preferences,
    isDark,
    isSyncing,
    updatePreferences,
    resetToDefaults,
    syncWithServer,
    // Convenience setters
    setThemeMode: (mode) => updatePreferences({ theme_mode: mode }),
    setAccentTheme: (accent) => updatePreferences({ accent_theme: accent }),
    setDensity: (density) => updatePreferences({ density }),
    setSidebarCollapsed: (collapsed) => updatePreferences({ sidebar_collapsed: collapsed }),
    setCardRadius: (radius) => updatePreferences({ card_radius: radius }),
    setReducedMotion: (reduced) => updatePreferences({ reduced_motion: reduced }),
    setHighContrast: (contrast) => updatePreferences({ high_contrast: contrast }),
    setDefaultLandingDashboard: (path) => updatePreferences({ default_landing_dashboard: path }),
  };

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
