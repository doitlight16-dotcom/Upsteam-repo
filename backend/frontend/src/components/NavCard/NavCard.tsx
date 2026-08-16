import type { ReactNode } from 'react';
import { Link } from 'react-router-dom';
import styles from './NavCard.module.css';

export interface NavCardProps {
  to: string;
  icon: ReactNode;
  title: string;
  description: string;
}

/**
 * Крупная тайл-кнопка главного экрана. Целиком кликабельна (весь Link),
 * а не только текст — важно для попадания пальцем на мобильном экране.
 */
export function NavCard({ to, icon, title, description }: NavCardProps) {
  return (
    <Link to={to} className={styles.card}>
      <span className={styles.icon} aria-hidden="true">
        {icon}
      </span>
      <span className={styles.title}>{title}</span>
      <span className={styles.description}>{description}</span>
    </Link>
  );
}
