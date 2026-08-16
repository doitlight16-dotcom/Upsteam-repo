import type { WhiteLabelConfig } from '../types';
import type { TelegramThemeParams } from '../types/telegram';

/**
 * Пишет бренд-цвета White Label конфига в CSS custom properties.
 * Вызывается один раз в App.tsx, когда конфиг загружен.
 */
export function applyBrandTheme(config: WhiteLabelConfig): void {
  const root = document.documentElement.style;
  root.setProperty('--brand-primary', config.primaryColor);
  root.setProperty('--brand-secondary', config.secondaryColor);
}

/**
 * Пишет Telegram themeParams в CSS custom properties, если приложение
 * открыто внутри Telegram. Вне Telegram переменные остаются на значениях
 * по умолчанию из styles/global.css (светлая тема).
 */
export function applyTelegramTheme(themeParams: TelegramThemeParams | undefined): void {
  if (!themeParams) return;

  const root = document.documentElement.style;
  const map: Record<string, string | undefined> = {
    '--tg-bg-color': themeParams.bg_color,
    '--tg-text-color': themeParams.text_color,
    '--tg-hint-color': themeParams.hint_color,
    '--tg-link-color': themeParams.link_color,
    '--tg-button-color': themeParams.button_color,
    '--tg-button-text-color': themeParams.button_text_color,
    '--tg-secondary-bg-color': themeParams.secondary_bg_color,
    '--tg-header-bg-color': themeParams.header_bg_color,
    '--tg-section-bg-color': themeParams.section_bg_color,
    '--tg-subtitle-text-color': themeParams.subtitle_text_color,
  };

  for (const [cssVar, value] of Object.entries(map)) {
    if (value) root.setProperty(cssVar, value);
  }
}
