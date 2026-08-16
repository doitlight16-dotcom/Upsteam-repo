import { useNavigate } from 'react-router-dom';
import styles from './PageHeader.module.css';

export interface PageHeaderProps {
  title: string;
}

/**
 * Заголовок подстраницы со стрелкой "назад".
 *
 * Дублирует функциональность нативного Telegram BackButton (см.
 * hooks/useBackButton.ts) намеренно: у Telegram-клиента кнопка "Назад"
 * рисуется в шапке нативного окна и не видна при превью в обычном браузере
 * (например, во время разработки), поэтому на самой странице всегда есть
 * запасной вариант.
 */
export function PageHeader({ title }: PageHeaderProps) {
  const navigate = useNavigate();

  return (
    <header className={styles.header}>
      <button
        type="button"
        className={styles.backButton}
        onClick={() => navigate('/')}
        aria-label="Назад на главный экран"
      >
        ←
      </button>
      <h1 className={styles.title}>{title}</h1>
    </header>
  );
}
