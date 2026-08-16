import { useEffect, useMemo, useState } from 'react';
import type { TelegramThemeParams, TelegramWebAppUser } from '../types/telegram';

export interface UseTelegramResult {
  /** true, если приложение реально открыто внутри Telegram. */
  isTelegram: boolean;
  user: TelegramWebAppUser | null;
  colorScheme: 'light' | 'dark';
  themeParams: TelegramThemeParams | undefined;
  initData: string;
  /**
   * Открывает ссылку на пользователя/канал.
   * - `https://t.me/...` — через нативный WebApp.openTelegramLink (или window.open вне Telegram).
   * - `tg://...` — прямой переход по ссылке (перехватывается Telegram-клиентом на устройстве);
   *   вне Telegram-клиента такая ссылка не сработает, это ожидаемое ограничение.
   */
  openTelegramLink: (url: string) => void;
  /** Открывает внешнюю ссылку (сайт, презентация) в системном браузере. */
  openExternalLink: (url: string) => void;
  hapticSelection: () => void;
}

/**
 * Единая точка входа в Telegram WebApp SDK.
 *
 * Инициализация (`ready`, `expand`) выполняется один раз при первом монтировании.
 * Если window.Telegram отсутствует (приложение открыто в обычном браузере
 * при разработке или превью), хук не бросает исключение — просто отдаёт
 * безопасные значения по умолчанию, чтобы остальной код не проверял
 * "а вдруг Telegram нет" в каждом компоненте.
 */
export function useTelegram(): UseTelegramResult {
  const webApp = useMemo(() => window.Telegram?.WebApp ?? null, []);
  const [colorScheme, setColorScheme] = useState<'light' | 'dark'>(webApp?.colorScheme ?? 'light');

  useEffect(() => {
    if (!webApp) return;

    webApp.ready();
    try {
      webApp.expand();
    } catch (e) {
      console.warn('Failed to expand webapp', e);
    }

    const handleThemeChange = () => setColorScheme(webApp.colorScheme);
    webApp.onEvent('themeChanged', handleThemeChange);
    return () => webApp.offEvent('themeChanged', handleThemeChange);
  }, [webApp]);

  return {
    isTelegram: webApp !== null,
    user: webApp?.initDataUnsafe.user ?? null,
    colorScheme,
    themeParams: webApp?.themeParams,
    initData: webApp?.initData ?? '',
    openTelegramLink: (url: string) => {
      if (url.startsWith('tg://')) {
        window.location.href = url;
        return;
      }
      if (webApp) {
        webApp.openTelegramLink(url);
      } else {
        window.open(url, '_blank', 'noopener,noreferrer');
      }
    },
    openExternalLink: (url: string) => {
      if (webApp) {
        webApp.openLink(url);
      } else {
        window.open(url, '_blank', 'noopener,noreferrer');
      }
    },
    hapticSelection: () => {
      webApp?.HapticFeedback.selectionChanged();
    },
  };
}
