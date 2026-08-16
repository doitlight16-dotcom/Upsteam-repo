/**
 * Конфигурация White Label — бренд клиента, который "купил" это приложение.
 *
 * Сейчас значения приходят из статического объекта (config/whiteLabel.ts).
 * Форма типа спроектирована так, чтобы в будущем её без изменений мог
 * отдавать backend-эндпоинт (см. api/whiteLabelApi.ts).
 */
export interface WhiteLabelConfig {
  companyName: string;
  companyDescription: string;
  /** Абсолютный URL логотипа (PNG/SVG). */
  logoUrl: string;
  /** HEX-цвет, например "#2AABEE". */
  primaryColor: string;
  /** HEX-цвет, используется для второстепенных акцентов. */
  secondaryColor: string;
  /** Список услуг/пунктов оффера — рендерится списком на странице "О компании". */
  services: string[];
  websiteUrl: string;
  /** Ссылка на презентацию (PDF/слайды). Может отсутствовать. */
  presentationUrl?: string;
}
