/**
 * Тонкая обёртка над fetch для будущих запросов к backend.
 *
 * Базовый URL берётся из VITE_API_BASE_URL (.env). Пока ни один
 * Http*Api-класс реально не используется в приложении (везде включены
 * Mock*Api, см. api/index.ts) — этот файл существует, чтобы подключение
 * настоящего backend было заменой одной строки, а не написанием нового кода.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '';

export class ApiError extends Error {
  readonly status?: number;

  constructor(message: string, status?: number) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
  }
}

export interface ApiFetchOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  /** initData из Telegram WebApp — backend валидирует им сессию (см. MultiTenancyMiddleware). */
  telegramInitData?: string;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  if (!API_BASE_URL) {
    throw new ApiError(
      `VITE_API_BASE_URL не задан — нельзя выполнить запрос к ${path}. ` +
        'Задайте переменную окружения или используйте Mock*Api.',
    );
  }

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };
  if (options.telegramInitData) {
    headers['Authorization'] = `Bearer ${options.telegramInitData}`;
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: options.method ?? 'GET',
      headers,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
  } catch {
    throw new ApiError('Сеть недоступна. Проверьте подключение и попробуйте ещё раз.');
  }

  if (!response.ok) {
    throw new ApiError(`Запрос завершился с ошибкой (${response.status})`, response.status);
  }

  return (await response.json()) as T;
}
