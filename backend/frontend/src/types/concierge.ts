/**
 * Данные, которые фронтенд отправляет при вопросе консьержу.
 *
 * telegramUser / initData прикладываются, чтобы бэкенд в будущем мог
 * провалидировать сессию (см. MultiTenancyMiddleware) и понять, кто задал
 * вопрос, не спрашивая у пользователя имя ещё раз.
 */
export interface ConciergeQuestionInput {
  question: string;
  telegramUser?: {
    id: number;
    firstName: string;
    username?: string;
  };
}

export interface ConciergeQuestionResult {
  success: boolean;
  /** Человекочитаемое сообщение для отображения пользователю. */
  message: string;
}

export interface FaqItem {
  id: string;
  question: string;
  answer: string;
}
