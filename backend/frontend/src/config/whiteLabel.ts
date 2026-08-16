import type { WhiteLabelConfig } from '../types';

/**
 * Дефолтный White Label конфиг — бренд КМГ для ADIPEC Concierge.
 *
 * Это единственное место в приложении, где «зашит» бренд конкретного
 * клиента. Ни один компонент/страница не должны содержать имя компании,
 * цвет или ссылку напрямую — только через этот объект.
 */
export const defaultWhiteLabelConfig: WhiteLabelConfig = {
  companyName: 'КазМунайГаз',
  companyDescription:
    'АО «НК «КазМунайГаз» — ведущая вертикально-интегрированная нефтегазовая компания Казахстана. Мы объединяем передовые технологии и стратегическое управление активами для максимизации возврата на инвестиции в энергетическом секторе.',
  logoUrl: '/logo-kmg.svg',
  primaryColor: '#D4AF37',
  secondaryColor: '#B8941F',
  services: [
    'Industrial AI & Predictive Maintenance',
    'Big Data Analytics для нефтегазовой отрасли',
    'Кибербезопасность критической инфраструктуры',
    'Синдикативные закупки премиального транспорта',
    'Офплан-инвестиции в недвижимость ОАЭ',
  ],
  websiteUrl: 'https://www.kmg.kz',
  presentationUrl: 'https://www.kmg.kz/upload/files/white-paper-adipec.pdf',
};
