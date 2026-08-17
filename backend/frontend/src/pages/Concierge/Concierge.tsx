import { useState, type FormEvent } from 'react';
import { PageHeader, Button, ErrorState } from '../../components';
import { useBackButton } from '../../hooks/useBackButton';
import { useTelegram } from '../../hooks/useTelegram';
import { conciergeApi } from '../../api';
import { mockFaq } from '../../data/mockFaq';
import styles from './Concierge.module.css';

type SubmitStatus = 'idle' | 'submitting' | 'success' | 'error';

const MAX_QUESTION_LENGTH = 500;

export function Concierge() {
  useBackButton();
  const { user, initData } = useTelegram();
  const [question, setQuestion] = useState('');
  const [status, setStatus] = useState<SubmitStatus>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const trimmedQuestion = question.trim();
  const isValid = trimmedQuestion.length > 0 && trimmedQuestion.length <= MAX_QUESTION_LENGTH;

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    if (!isValid || status === 'submitting') return;

    setStatus('submitting');
    setErrorMessage('');

    try {
      const result = await conciergeApi.submitQuestion({
        question: trimmedQuestion,
        telegramUser: user
          ? { id: user.id, firstName: user.first_name, username: user.username }
          : undefined,
      });
      setSuccessMessage(result.message);
      setStatus('success');
      setQuestion('');
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : 'Не удалось отправить вопрос');
      setStatus('error');
    }
  }

  return (
    <div className="screen">
      <PageHeader title="Задать вопрос консьержу" />

      {status === 'success' ? (
        <div className={styles.successBox} role="status">
          <span className={styles.successIcon} aria-hidden="true">
            ✅
          </span>
          <p className={styles.successText}>{successMessage}</p>
          <Button variant="secondary" onClick={() => setStatus('idle')}>
            Задать ещё один вопрос
          </Button>
        </div>
      ) : (
        <form className={styles.form} onSubmit={handleSubmit}>
          <label className={styles.label} htmlFor="concierge-question">
            Ваш вопрос организаторам
          </label>
          <textarea
            id="concierge-question"
            className={styles.textarea}
            placeholder="Например: во сколько открывается регистрация?"
            value={question}
            maxLength={MAX_QUESTION_LENGTH}
            onChange={(event) => setQuestion(event.target.value)}
            rows={5}
          />
          <div className={styles.counter}>
            {trimmedQuestion.length}/{MAX_QUESTION_LENGTH}
          </div>

          {status === 'error' && (
            <ErrorState message={errorMessage} onRetry={() => setStatus('idle')} />
          )}

          <Button type="submit" fullWidth disabled={!isValid || status === 'submitting'}>
            {status === 'submitting' ? 'Отправляем...' : 'Отправить'}
          </Button>

          {!initData && (
            <p className={styles.hint}>
              Приложение открыто вне Telegram — вопрос будет отправлен без привязки к вашему
              Telegram-аккаунту.
            </p>
          )}
        </form>
      )}

      {mockFaq.length > 0 && (
        <section className={styles.faq}>
          <h2 className={styles.faqTitle}>Частые вопросы</h2>
          <ul className={styles.faqList}>
            {mockFaq.map((item) => (
              <li key={item.id} className={styles.faqItem}>
                <p className={styles.faqQuestion}>{item.question}</p>
                <p className={styles.faqAnswer}>{item.answer}</p>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  );
}
