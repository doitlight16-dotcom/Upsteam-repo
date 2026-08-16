import { useCallback, useEffect, useState } from 'react';

type AsyncState<T> =
  | { status: 'loading'; data: null; error: null }
  | { status: 'success'; data: T; error: null }
  | { status: 'error'; data: null; error: string };

/**
 * Оборачивает Promise-возвращающую функцию (обычно вызов api/*Api) в
 * loading/success/error состояние + функцию reload для повторной попытки.
 * Используется страницами Schedule и Participants, чтобы не дублировать
 * один и тот же useEffect+useState в обеих.
 */
export function useAsyncData<T>(loader: () => Promise<T>): AsyncState<T> & { reload: () => void } {
  const [state, setState] = useState<AsyncState<T>>({ status: 'loading', data: null, error: null });

  const load = useCallback(() => {
    setState({ status: 'loading', data: null, error: null });
    loader()
      .then((data) => setState({ status: 'success', data, error: null }))
      .catch((error: unknown) => {
        const message = error instanceof Error ? error.message : 'Не удалось загрузить данные';
        setState({ status: 'error', data: null, error: message });
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return { ...state, reload: load };
}
