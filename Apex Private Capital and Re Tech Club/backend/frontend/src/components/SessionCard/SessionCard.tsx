import type { Session } from '../../types';
import styles from './SessionCard.module.css';

export interface SessionCardProps {
  session: Session;
}

export function SessionCard({ session }: SessionCardProps) {
  return (
    <li className={styles.card}>
      <div className={styles.time}>
        {session.startTime}
        {session.endTime ? `–${session.endTime}` : ''}
      </div>
      <div className={styles.body}>
        <p className={styles.title}>{session.title}</p>
        <p className={styles.speaker}>
          {session.speakerName}
          {session.speakerRole ? `, ${session.speakerRole}` : ''}
        </p>
        {session.location && <p className={styles.location}>{session.location}</p>}
      </div>
    </li>
  );
}
