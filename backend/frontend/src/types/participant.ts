/**
 * Участник конференции, доступный в разделе "Нетворкинг".
 *
 * Контакт выражен двумя необязательными полями, потому что бэкенд в будущем
 * может отдавать либо username, либо только numeric id — компонент карточки
 * сам решает, как построить deep link (см. utils/telegramLink.ts).
 */
export interface Participant {
  id: string;
  fullName: string;
  role: string;
  bio: string;
  avatarUrl?: string;
  telegramUsername?: string;
  telegramUserId?: number;
}
