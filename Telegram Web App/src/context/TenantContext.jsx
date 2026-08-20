/**
 * TenantContext — Dynamic White-Label Theme Provider
 * ===================================================
 * Fetches tenant branding config from the API and injects
 * CSS custom properties into :root for dynamic theming.
 *
 * Usage:
 *   <TenantProvider tenantId="default">
 *     <App />
 *   </TenantProvider>
 *
 *   const { tenant, colors, fonts, loading } = useTenant();
 */

import React, { createContext, useContext, useState, useEffect } from "react";

// ── Default theme (mirrors the hardcoded C object from App.jsx) ──
const DEFAULT_COLORS = {
  bg: "#141210",
  surface: "#1C1812",
  surfaceHi: "#242017",
  border: "#39311F",
  borderHi: "#4E4327",
  gold: "#C9A227",
  goldBright: "#E9CA73",
  text: "#F1EAD9",
  textMuted: "#9C9384",
  textFaint: "#6E6656",
  accentDanger: "#9C3F35",
  accentSuccess: "#748A6C",
};

const DEFAULT_FONTS = {
  display: "'Fraunces', serif",
  body: "'Manrope', sans-serif",
  mono: "'IBM Plex Mono', monospace",
};

const DEFAULT_TENANT = {
  tenant_id: "default",
  brand_name: "APEX ASSET SUITE",
  event_name: "ADIPEC Concierge",
  tagline: "АО «НК «КазМунайГаз» · закрытый доступ делегатов",
  colors: DEFAULT_COLORS,
  fonts: DEFAULT_FONTS,
  contact: {
    support_username: "@appex_support",
    support_phone: "+971500000000",
    support_hours: "10:00–20:00 (UTC+4)",
  },
  logo_url: null,
  banner_url: null,
};

// ── Map API snake_case fields to CSS-friendly camelCase ──
function normalizeColors(apiColors) {
  if (!apiColors) return DEFAULT_COLORS;
  return {
    bg: apiColors.bg || DEFAULT_COLORS.bg,
    surface: apiColors.surface || DEFAULT_COLORS.surface,
    surfaceHi: apiColors.surface_hi || apiColors.surfaceHi || DEFAULT_COLORS.surfaceHi,
    border: apiColors.border || DEFAULT_COLORS.border,
    borderHi: apiColors.border_hi || apiColors.borderHi || DEFAULT_COLORS.borderHi,
    gold: apiColors.gold || DEFAULT_COLORS.gold,
    goldBright: apiColors.gold_bright || apiColors.goldBright || DEFAULT_COLORS.goldBright,
    text: apiColors.text || DEFAULT_COLORS.text,
    textMuted: apiColors.text_muted || apiColors.textMuted || DEFAULT_COLORS.textMuted,
    textFaint: apiColors.text_faint || apiColors.textFaint || DEFAULT_COLORS.textFaint,
    accentDanger: apiColors.accent_danger || apiColors.accentDanger || DEFAULT_COLORS.accentDanger,
    accentSuccess: apiColors.accent_success || apiColors.accentSuccess || DEFAULT_COLORS.accentSuccess,
  };
}

function normalizeFonts(apiFonts) {
  if (!apiFonts) return DEFAULT_FONTS;
  return {
    display: apiFonts.display || DEFAULT_FONTS.display,
    body: apiFonts.body || DEFAULT_FONTS.body,
    mono: apiFonts.mono || DEFAULT_FONTS.mono,
  };
}

// ── Context ──
const TenantContext = createContext({
  tenant: DEFAULT_TENANT,
  colors: DEFAULT_COLORS,
  fonts: DEFAULT_FONTS,
  loading: true,
  updateTenant: () => {},
});

export function useTenant() {
  return useContext(TenantContext);
}

// ── CSS Variable Injector ──
function injectCSSVariables(colors, fonts) {
  const root = document.documentElement;

  // Colors
  root.style.setProperty("--color-bg", colors.bg);
  root.style.setProperty("--color-surface", colors.surface);
  root.style.setProperty("--color-surface-hi", colors.surfaceHi);
  root.style.setProperty("--color-border", colors.border);
  root.style.setProperty("--color-border-hi", colors.borderHi);
  root.style.setProperty("--color-gold", colors.gold);
  root.style.setProperty("--color-gold-bright", colors.goldBright);
  root.style.setProperty("--color-text", colors.text);
  root.style.setProperty("--color-text-muted", colors.textMuted);
  root.style.setProperty("--color-text-faint", colors.textFaint);
  root.style.setProperty("--color-accent-danger", colors.accentDanger);
  root.style.setProperty("--color-accent-success", colors.accentSuccess);

  // Fonts
  root.style.setProperty("--font-display", fonts.display);
  root.style.setProperty("--font-body", fonts.body);
  root.style.setProperty("--font-mono", fonts.mono);
}

// ── Provider Component ──
const API_BASE = import.meta.env.VITE_API_BASE || "";

export function TenantProvider({ tenantId = "default", children }) {
  const [tenant, setTenant] = useState(DEFAULT_TENANT);
  const [loading, setLoading] = useState(true);

  const colors = normalizeColors(tenant.colors);
  const fonts = normalizeFonts(tenant.fonts);

  // Fetch tenant config from API
  useEffect(() => {
    let cancelled = false;

    async function fetchConfig() {
      try {
        const res = await fetch(`${API_BASE}/api/tenant/${tenantId}`);
        if (res.ok) {
          const data = await res.json();
          if (!cancelled) {
            setTenant({ ...DEFAULT_TENANT, ...data });
          }
        }
      } catch (err) {
        console.warn("Failed to fetch tenant config, using defaults:", err.message);
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    fetchConfig();
    return () => { cancelled = true; };
  }, [tenantId]);

  // Inject CSS variables whenever tenant config changes
  useEffect(() => {
    injectCSSVariables(colors, fonts);
  }, [colors, fonts]);

  // Live update function for admin panel
  const updateTenant = (newConfig) => {
    setTenant((prev) => ({ ...prev, ...newConfig }));
  };

  return (
    <TenantContext.Provider value={{ tenant, colors, fonts, loading, updateTenant }}>
      {children}
    </TenantContext.Provider>
  );
}

export { DEFAULT_COLORS, DEFAULT_FONTS, DEFAULT_TENANT };
