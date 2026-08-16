import { PageHeader, LoadingState, ErrorState, EmptyState, SessionCard } from '../../components';
import { useAsyncData } from '../../hooks/useAsyncData';
import { useBackButton } from '../../hooks/useBackButton';
import { scheduleApi } from '../../api';
import type { Session } from '../../types';
import styles from './Schedule.module.css';

function groupByDate(sessions: Session[]): Map<string, Session[]> {
  const groups = new Map<string, Session[]>();
  for (const session of sessions) {
    const list = groups.get(session.date) ?? [];
    list.push(session);
    groups.set(session.date, list);
  }
  return groups;
}

function formatDate(dateIso: string): string {
  return new Date(dateIso).toLocaleDateString('ru-RU', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });
}

export function Schedule() {
  useBackButton();
  const { status, data, error, reload } = useAsyncData(() => scheduleApi.getSessions());

  return (
    <div className="screen">
      <PageHeader title="Расписание и спикеры" />

      {status === 'loading' && <LoadingState message="Загружаем расписание..." />}
      {status === 'error' && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data.length === 0 && (
        <EmptyState message="Расписание пока не опубликовано." />
      )}
      {status === 'success' && data.length > 0 && (
        <>
          {Array.from(groupByDate(data)).map(([date, sessions]) => (
            <section key={date}>
              <h2 className={styles.dateHeading}>{formatDate(date)}</h2>
              <ul className={styles.list}>
                {sessions.map((session) => (
                  <SessionCard key={session.id} session={session} />
                ))}
              </ul>
            </section>
          ))}
        </>
      )}
    </div>
  );
}
