import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

/**
 * Показывает нативную кнопку "Назад" Telegram на всех экранах, кроме Home,
 * и уводит на переданный путь (по умолчанию — на главный экран) по клику.
 *
 * Вне Telegram ничего не делает: на подстраницах уже есть собственная
 * стрелка "назад" в PageHeader для браузерного превью.
 */
export function useBackButton(fallbackPath = '/'): void {
  const navigate = useNavigate();

  useEffect(() => {
    const webApp = window.Telegram?.WebApp;
    if (!webApp) return;

    const handleClick = () => navigate(fallbackPath);

    webApp.BackButton.show();
    webApp.BackButton.onClick(handleClick);

    return () => {
      webApp.BackButton.offClick(handleClick);
      webApp.BackButton.hide();
    };
  }, [navigate, fallbackPath]);
}
