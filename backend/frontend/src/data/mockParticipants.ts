import type { Participant } from '../types';

/**
 * Участники ADIPEC для раздела нетворкинга.
 * В продакшене будут приходить через backend API.
 */
export const mockParticipants: Participant[] = [
  {
    id: 'p-1',
    fullName: 'Нуржан Салимов',
    role: 'VP Digital Transformation, КМГ',
    bio: 'Руководит стратегией цифровой трансформации КазМунайГаз. 15 лет в нефтегазовой отрасли.',
    telegramUsername: 'n_salimov',
  },
  {
    id: 'p-2',
    fullName: 'Dr. Aigerim Dossanova',
    role: 'Chief Data Officer, Эмбамунайгаз',
    bio: 'Big Data и предиктивная аналитика для upstream-операций. PhD в Data Science (MIT).',
    telegramUsername: 'aigerim_cdo',
  },
  {
    id: 'p-3',
    fullName: 'Kanat Yermekbayev',
    role: 'CISO, Мангистаумунайгаз',
    bio: 'Кибербезопасность критической инфраструктуры. Ex-Kaspersky, CISSP certified.',
    telegramUsername: 'k_yermekbayev',
  },
  {
    id: 'p-4',
    fullName: 'Sultan Al-Mansoori',
    role: 'VP Partnerships, ADNOC',
    bio: 'Стратегические партнёрства ADNOC с международными NOC. Более 20 лет в отрасли.',
    telegramUsername: 'sultan_adnoc',
  },
  {
    id: 'p-5',
    fullName: 'Marie-Claire Dubois',
    role: 'Director M&A, TotalEnergies',
    bio: 'Трансграничные сделки M&A в энергетическом секторе. Базируется в Абу-Даби.',
    telegramUsername: 'mc_dubois',
  },
  {
    id: 'p-6',
    fullName: 'Нурислам Абдулла',
    role: 'Product Manager, Appex Asset Suite',
    bio: 'Разработка Telegram WebApp и цифровых продуктов для альтернативных инвестиций.',
    telegramUsername: 'nurislam_dev',
  },
  {
    id: 'p-7',
    fullName: 'Ясмина Каримова',
    role: 'Compliance & Product, Appex',
    bio: 'KYC/AML комплаенс, разработка инвестиционных продуктов для HNWI.',
    telegramUsername: 'yasmina_k',
  },
  {
    id: 'p-8',
    fullName: 'Ерлан Мустафин',
    role: 'Директор по закупкам, КМГ',
    bio: 'Стратегические закупки оборудования и синдикативный транспорт для дочерних структур.',
    telegramUserId: 112233445,
  },
];
