import { NavCard, Button } from '../../components';
import { useTelegram } from '../../hooks/useTelegram';
import styles from './Home.module.css';

const NAV_ITEMS = [
  {
    to: '/schedule',
    icon: '🗓️',
    title: 'Расписание',
    description: 'Сессии ADIPEC и доклады спикеров КМГ',
  },
  {
    to: '/participants',
    icon: '🤝',
    title: 'Нетворкинг',
    description: 'Делегаты и топ-менеджеры',
  },
  {
    to: '/concierge',
    icon: '💬',
    title: 'Консьерж',
    description: 'FAQ и связь с администратором',
  },
  {
    to: '/company',
    icon: '📄',
    title: 'Оффер',
    description: 'О компании и White Paper',
  },
] as const;

export function Home() {
  const { user, openExternalLink } = useTelegram();

  return (
    <div className="screen">
      <div className={styles.greeting}>
        <p className={styles.eyebrow}>ADIPEC Concierge</p>
        <h1 className={styles.title}>
          {user ? `Добро пожаловать, ${user.first_name}` : 'Добро пожаловать'}
        </h1>
        <div className={styles.vipBadge}>Oil & Gas Corporate Member</div>
      </div>

      <div className={styles.grid}>
        {NAV_ITEMS.map((item) => (
          <NavCard key={item.to} {...item} />
        ))}
      </div>

      <div className={styles.sosSection}>
        <Button
          variant="danger"
          fullWidth
          className={styles.sosButton}
          onClick={() => openExternalLink('tel:+97150000000')}
        >
          🆘 SOS / Экстренная связь
        </Button>
      </div>
    </div>
  );
}
