import styles from './LoadingState.module.css';

export interface LoadingStateProps {
  message?: string;
}

export function LoadingState({ message = 'Загрузка...' }: LoadingStateProps) {
  return (
    <div className={styles.wrapper} role="status" aria-live="polite">
      <span className={styles.spinner} aria-hidden="true" />
      <span className={styles.message}>{message}</span>
    </div>
  );
}
