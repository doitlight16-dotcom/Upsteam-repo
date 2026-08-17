import type { ConciergeQuestionInput, ConciergeQuestionResult } from '../types';
import { apiFetch } from './httpClient';

export interface ConciergeApi {
  submitQuestion(input: ConciergeQuestionInput): Promise<ConciergeQuestionResult>;
}

/**
 * Временная mock-реализация. Ничего никуда не отправляет — просто логирует
 * и возвращает успех, чтобы UI-флоу (форма → успех) можно было полностью
 * проверить до появления backend-эндпоинта.
 */
class MockConciergeApi implements ConciergeApi {
  async submitQuestion(input: ConciergeQuestionInput): Promise<ConciergeQuestionResult> {
    await new Promise((resolve) => setTimeout(resolve, 350));
    // eslint-disable-next-line no-console
    console.info('[MockConciergeApi] Вопрос принят (не отправлен на backend):', input);
    return {
      success: true,
      message: 'Вопрос отправлен. Мы ответим в ближайшее время.',
    };
  }
}

/**
 * Ожидаемый контракт backend-эндпоинта (нужно реализовать отдельно):
 *   POST /concierge/questions
 *   body: ConciergeQuestionInput
 *   response: ConciergeQuestionResult
 *
 * По ТЗ backend должен переслать вопрос в закрытый Telegram-чат
 * администратора (например, через Bot API sendMessage на стороне сервера).
 * Frontend только отправляет вопрос и telegramUser/initData для контекста —
 * пересылку в чат админа делает backend.
 */
class HttpConciergeApi implements ConciergeApi {
  async submitQuestion(input: ConciergeQuestionInput): Promise<ConciergeQuestionResult> {
    return apiFetch<ConciergeQuestionResult>('/concierge/questions', {
      method: 'POST',
      body: input,
    });
  }
}

export const mockConciergeApi = new MockConciergeApi();
export const httpConciergeApi = new HttpConciergeApi();

/** Активная реализация. Когда backend-эндпоинт готов — заменить на httpConciergeApi. */
export const conciergeApi: ConciergeApi = mockConciergeApi;
