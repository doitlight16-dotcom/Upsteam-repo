import type { Session } from '../types';
import { mockSchedule } from '../data/mockSchedule';
import { apiFetch } from './httpClient';

export interface ScheduleApi {
  getSessions(): Promise<Session[]>;
}

/** Имитирует задержку сети, чтобы loading-состояние страницы было видно и осмысленно в MVP. */
class MockScheduleApi implements ScheduleApi {
  async getSessions(): Promise<Session[]> {
    await new Promise((resolve) => setTimeout(resolve, 350));
    return [...mockSchedule].sort((a, b) =>
      `${a.date}T${a.startTime}`.localeCompare(`${b.date}T${b.startTime}`),
    );
  }
}

/**
 * Ожидаемый контракт backend-эндпоинта (ещё не реализован):
 *   GET /schedule/sessions -> Session[]
 * Формат Session — см. types/schedule.ts.
 */
class HttpScheduleApi implements ScheduleApi {
  async getSessions(): Promise<Session[]> {
    return apiFetch<Session[]>('/schedule/sessions');
  }
}

export const mockScheduleApi = new MockScheduleApi();
export const httpScheduleApi = new HttpScheduleApi();

/** Активная реализация. Когда backend-эндпоинт готов — заменить на httpScheduleApi. */
export const scheduleApi: ScheduleApi = mockScheduleApi;
