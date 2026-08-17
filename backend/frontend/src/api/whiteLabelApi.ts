import type { WhiteLabelConfig } from '../types';
import { defaultWhiteLabelConfig } from '../config/whiteLabel';
import { apiFetch } from './httpClient';

export interface WhiteLabelApi {
  getConfig(): Promise<WhiteLabelConfig>;
}

class MockWhiteLabelApi implements WhiteLabelApi {
  async getConfig(): Promise<WhiteLabelConfig> {
    return defaultWhiteLabelConfig;
  }
}

/**
 * Ожидаемый контракт backend-эндпоинта (ещё не реализован):
 *   GET /white-label/config -> WhiteLabelConfig
 * Позволит разработчику загружать логотип/цвета через админку без
 * пересборки frontend.
 */
class HttpWhiteLabelApi implements WhiteLabelApi {
  async getConfig(): Promise<WhiteLabelConfig> {
    return apiFetch<WhiteLabelConfig>('/white-label/config');
  }
}

export const mockWhiteLabelApi = new MockWhiteLabelApi();
export const httpWhiteLabelApi = new HttpWhiteLabelApi();

/** Активная реализация. Когда backend-эндпоинт готов — заменить на httpWhiteLabelApi. */
export const whiteLabelApi: WhiteLabelApi = mockWhiteLabelApi;
