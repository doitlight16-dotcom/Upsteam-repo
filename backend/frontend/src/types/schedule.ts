/**
 * Одна сессия/доклад в расписании конференции.
 */
export interface Session {
  id: string;
  /** Дата сессии в формате ISO (YYYY-MM-DD), используется для группировки по дням. */
  date: string;
  /** Время начала в формате HH:mm (24ч). */
  startTime: string;
  /** Время окончания в формате HH:mm (24ч). Необязательно. */
  endTime?: string;
  title: string;
  speakerName: string;
  /** Должность/компания спикера — короткая подпись под именем. */
  speakerRole?: string;
  /** Место проведения (зал/сцена), если у конференции несколько площадок. */
  location?: string;
}
