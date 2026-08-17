import { PageHeader, LoadingState, ErrorState, Button } from '../../components';
import { useAsyncData } from '../../hooks/useAsyncData';
import { useBackButton } from '../../hooks/useBackButton';
import { useTelegram } from '../../hooks/useTelegram';
import { whiteLabelApi } from '../../api';
import styles from './Company.module.css';

export function Company() {
  useBackButton();
  const { openExternalLink } = useTelegram();
  const { status, data: config, error, reload } = useAsyncData(() => whiteLabelApi.getConfig());

  return (
    <div className="screen">
      <PageHeader title="О компании" />

      {status === 'loading' && <LoadingState message="Загружаем информацию о компании..." />}
      {status === 'error' && <ErrorState message={error} onRetry={reload} />}

      {status === 'success' && (
        <>
          <div className={styles.brand}>
            <img src={config.logoUrl} alt={config.companyName} className={styles.logo} />
            <h1 className={styles.name}>{config.companyName}</h1>
          </div>

          <p className={styles.description}>{config.companyDescription}</p>

          {config.services.length > 0 && (
            <section className={styles.services}>
              <h2 className={styles.sectionTitle}>Услуги</h2>
              <ul className={styles.serviceList}>
                {config.services.map((service) => (
                  <li key={service} className={styles.serviceItem}>
                    {service}
                  </li>
                ))}
              </ul>
            </section>
          )}

          <div className={styles.actions}>
            <Button fullWidth onClick={() => openExternalLink(config.websiteUrl)}>
              Перейти на сайт
            </Button>
            {config.presentationUrl && (
              <Button
                variant="secondary"
                fullWidth
                onClick={() => openExternalLink(config.presentationUrl!)}
              >
                Открыть презентацию
              </Button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
