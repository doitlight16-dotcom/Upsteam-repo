# Appex Asset Suite — Frontend (Telegram Web App)

MVP-фронтенд для Telegram Mini App конференции: расписание, нетворкинг участников,
вопрос консьержу и White Label страница компании. React + Vite + TypeScript.

## Запуск

```bash
cd frontend
npm install
npm run dev
```

Откроется `http://localhost:5173`. Приложение полностью работает и вне Telegram
(в обычном браузере) — Telegram-специфичные функции (тема, initData, BackButton,
deep links) просто не активируются, ошибок не будет.

Проверка типов и продакшн-сборка:

```bash
npm run build      # tsc -b && vite build
npm run preview    # локальный просмотр собранного билда
```

## Переменные окружения

Скопируйте `.env.example` в `.env`, если/когда появится реальный backend API:

```bash
cp .env.example .env
```

Пока `VITE_API_BASE_URL` не нужен — все данные идут из mock (`src/data/`).

## Структура

```
src/
├── api/          # интерфейс + Mock/Http реализация на каждый домен данных
├── components/   # переиспользуемые UI-компоненты (Button, карточки, состояния)
├── config/       # White Label конфиг + применение темы (CSS-переменные)
├── data/         # mock-данные, полностью отделены от UI и от api/*
├── hooks/        # useTelegram, useBackButton, useAsyncData
├── pages/        # Home, Schedule, Participants, Concierge, Company
├── styles/       # глобальные design tokens
├── types/        # доменные типы + typings window.Telegram.WebApp
├── utils/        # сборка Telegram deep link
├── App.tsx       # роутинг (HashRouter) + загрузка White Label конфига
└── main.tsx
```

## Как переключить mock → реальный backend

Для каждого домена (`schedule`, `participants`, `concierge`, `whiteLabel`) уже
реализованы **два** класса, оба удовлетворяют одному интерфейсу:

- `Mock*Api` — использует данные из `src/data/*`, активен сейчас.
- `Http*Api` — уже написан, дергает `apiFetch()` по ожидаемому пути, ждёт
  реального эндпоинта.

Переключение — правка одной строки экспорта в конце каждого файла
`src/api/*.ts`:

```ts
// было
export const scheduleApi: ScheduleApi = mockScheduleApi;
// стало
export const scheduleApi: ScheduleApi = httpScheduleApi;
```

Компоненты и страницы импортируют только `scheduleApi` (и т. п.) из `src/api`,
поэтому их код не меняется вообще.

## Ожидаемые backend-эндпоинты (пока не реализованы)

Ничего из этого не создавалось на бэкенде — только задокументирован контракт,
который ждёт `Http*Api`:

| Эндпоинт | Метод | Возвращает | Для чего |
|---|---|---|---|
| `/schedule/sessions` | GET | `Session[]` | Расписание конференции |
| `/participants` | GET | `Participant[]` | Список участников для нетворкинга |
| `/concierge/questions` | POST | `ConciergeQuestionResult` | Приём вопроса, дальше backend пересылает его в закрытый Telegram-чат админа |
| `/white-label/config` | GET | `WhiteLabelConfig` | Логотип/цвета/бренд без пересборки frontend |

Формы типов — в `src/types/`.

## Что mock, что готово к подключению

- **Полностью mock:** расписание, участники, White Label конфиг, вопрос
  консьержу — везде включена `Mock*Api`, никакие сетевые запросы наружу не уходят.
- **Готово к подключению:** `Http*Api` для всех четырёх доменов уже написаны
  и типизированы, ждут реальных эндпоинтов backend.
- **FAQ** на экране консьержа — статический список из `src/data/mockFaq.ts`,
  без отдельной системы/API (по ТЗ — опционально и просто).

## Telegram Web App интеграция

- Инициализация (`ready()`, `expand()`), пользователь, `colorScheme`,
  `themeParams`, `initData` — через `useTelegram()`.
- Нативная кнопка "Назад" — через `useBackButton()` на всех экранах, кроме Home.
- Тема Telegram (`themeParams`) и бренд White Label — два независимых слоя
  CSS-переменных, см. `src/config/applyTheme.ts` и `src/styles/global.css`.
- Приложение не падает при открытии вне Telegram: весь доступ к
  `window.Telegram.WebApp` — только через `useTelegram()`, которая отдаёт
  безопасные дефолты, если `window.Telegram` не существует.
- Роутинг — `HashRouter` (не `BrowserRouter`): SPA раздаётся статически, без
  серверной конфигурации для rewrite, что важно для WebView Telegram.
