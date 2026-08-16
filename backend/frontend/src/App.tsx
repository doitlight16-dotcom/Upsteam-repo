import { HashRouter, Routes, Route } from 'react-router-dom';
import { useEffect } from 'react';
import { Home, Schedule, Participants, Concierge, Company } from './pages';
import { LoadingState, ErrorState } from './components';
import { useAsyncData } from './hooks/useAsyncData';
import { useTelegram } from './hooks/useTelegram';
import { whiteLabelApi } from './api';
import { applyBrandTheme, applyTelegramTheme } from './config/applyTheme';

/**
 * Загружает White Label конфиг один раз при старте приложения и применяет
 * его как CSS-переменные — до этого момента компоненты ниже не рендерятся,
 * чтобы не было "мигания" дефолтным брендом.
 *
 * Telegram themeParams применяются отдельным эффектом, независимо от
 * White Label — это два разных источника цвета (см. config/applyTheme.ts).
 */
export function App() {
  const { themeParams } = useTelegram();
  const { status, data: config, error, reload } = useAsyncData(() => whiteLabelApi.getConfig());

  useEffect(() => {
    applyTelegramTheme(themeParams);
  }, [themeParams]);

  useEffect(() => {
    if (config) applyBrandTheme(config);
  }, [config]);

  if (status === 'loading') {
    return <LoadingState message="Загружаем приложение..." />;
  }

  if (status === 'error') {
    return <ErrorState message={error} onRetry={reload} />;
  }

  return (
    <HashRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/schedule" element={<Schedule />} />
        <Route path="/participants" element={<Participants />} />
        <Route path="/concierge" element={<Concierge />} />
        <Route path="/company" element={<Company />} />
      </Routes>
    </HashRouter>
  );
}
