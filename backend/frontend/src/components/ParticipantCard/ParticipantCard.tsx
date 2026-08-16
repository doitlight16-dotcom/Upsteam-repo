import type { Participant } from '../../types';
import { buildTelegramDeepLink } from '../../utils/telegramLink';
import { useTelegram } from '../../hooks/useTelegram';
import { Button } from '../Button/Button';
import styles from './ParticipantCard.module.css';

export interface ParticipantCardProps {
  participant: Participant;
}

function getInitials(fullName: string): string {
  return fullName
    .split(' ')
    .slice(0, 2)
    .map((part) => part.charAt(0).toUpperCase())
    .join('');
}

export function ParticipantCard({ participant }: ParticipantCardProps) {
  const { openTelegramLink } = useTelegram();
  const deepLink = buildTelegramDeepLink(participant);

  return (
    <li className={styles.card}>
      <div className={styles.avatar} aria-hidden="true">
        {participant.avatarUrl ? (
          <img src={participant.avatarUrl} alt="" className={styles.avatarImg} />
        ) : (
          getInitials(participant.fullName)
        )}
      </div>
      <div className={styles.info}>
        <p className={styles.name}>{participant.fullName}</p>
        <p className={styles.role}>{participant.role}</p>
        <p className={styles.bio}>{participant.bio}</p>
      </div>
      {deepLink && (
        <Button
          variant="secondary"
          className={styles.messageButton}
          onClick={() => openTelegramLink(deepLink)}
        >
          Написать
        </Button>
      )}
    </li>
  );
}
