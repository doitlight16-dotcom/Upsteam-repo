import { PageHeader, LoadingState, ErrorState, EmptyState, ParticipantCard } from '../../components';
import { useAsyncData } from '../../hooks/useAsyncData';
import { useBackButton } from '../../hooks/useBackButton';
import { participantsApi } from '../../api';
import styles from './Participants.module.css';

export function Participants() {
  useBackButton();
  const { status, data, error, reload } = useAsyncData(() => participantsApi.getParticipants());

  return (
    <div className="screen">
      <PageHeader title="Участники" />

      {status === 'loading' && <LoadingState message="Загружаем участников..." />}
      {status === 'error' && <ErrorState message={error} onRetry={reload} />}
      {status === 'success' && data.length === 0 && (
        <EmptyState message="Пока никто из участников не зарегистрирован." />
      )}
      {status === 'success' && data.length > 0 && (
        <ul className={styles.list}>
          {data.map((participant) => (
            <ParticipantCard key={participant.id} participant={participant} />
          ))}
        </ul>
      )}
    </div>
  );
}
