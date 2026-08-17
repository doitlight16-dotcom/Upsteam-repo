import type { Participant } from '../types';

/**
 * Строит deep link на личный чат с участником.
 *
 * Приоритет — username (`https://t.me/username`): открывается везде
 * (Telegram, обычный браузер, любая ОС) и не требует, чтобы у зрителя
 * уже был Telegram-клиент, настроенный на кастомную схему. `tg://user?id=`
 * используется как запасной вариант, когда backend отдал только numeric id
 * (например, участник не задал username в Telegram) — этот вариант
 * работает только внутри установленного Telegram-клиента.
 *
 * Возвращает null, если ни username, ни id недоступны — тогда UI не должен
 * показывать кнопку "Написать".
 */
export function buildTelegramDeepLink(participant: Participant): string | null {
  if (participant.telegramUsername) {
    return `https://t.me/${participant.telegramUsername}`;
  }
  if (participant.telegramUserId) {
    return `tg://user?id=${participant.telegramUserId}`;
  }
  return null;
}
