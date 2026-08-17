import type { Participant } from '../types';
import { mockParticipants } from '../data/mockParticipants';
import { apiFetch } from './httpClient';

export interface ParticipantsApi {
  getParticipants(): Promise<Participant[]>;
}

class MockParticipantsApi implements ParticipantsApi {
  async getParticipants(): Promise<Participant[]> {
    await new Promise((resolve) => setTimeout(resolve, 350));
    return mockParticipants;
  }
}

/**
 * Ожидаемый контракт backend-эндпоинта (ещё не реализован):
 *   GET /participants -> Participant[]
 * Формат Participant — см. types/participant.ts. Важно: username участника
 * должен приходить только для тех, кто согласился быть видимым в нетворкинге
 * (opt-in), это решение уровня backend, не frontend.
 */
class HttpParticipantsApi implements ParticipantsApi {
  async getParticipants(): Promise<Participant[]> {
    return apiFetch<Participant[]>('/participants');
  }
}

export const mockParticipantsApi = new MockParticipantsApi();
export const httpParticipantsApi = new HttpParticipantsApi();

/** Активная реализация. Когда backend-эндпоинт готов — заменить на httpParticipantsApi. */
export const participantsApi: ParticipantsApi = mockParticipantsApi;
