# TG-Monitoring

Сервис мониторинга упоминаний компании, персоны или события в соцсетях, форумах, блогах и СМИ с доставкой результатов в Telegram.

## Возможности

- **Мониторинговый сайт** — информация о компании и услугах
- **Предпросмотр упоминаний** — пользователь вводит поисковый запрос и видит найденные сообщения до заказа доступа
- **Telegram** — автоматическая отправка новых упоминаний

## Структура

```
apps/
  web/   — React + TypeScript (Vite)
  api/   — FastAPI + Playwright (brandanalytics.ru)
```

## Быстрый старт

### Backend

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
playwright install chromium
copy .env.example .env
# заполните BR_ANALYTICS_LOGIN / BR_ANALYTICS_PASSWORD
uvicorn app.main:app --reload
```

### Frontend

```powershell
cd apps/web
npm install
npm run dev
```

## Предпросмотр

Эндпоинт `POST /api/v1/preview/search` с телом `{ "query": "..." }`:

1. Логин на `bra...lytics.ru/account/login/`
2. Открытие темы «Энергострой» для оценки объёма (или «Добавить новую тему», если её нет)
3. Вставка запроса в `#key_words_operator`
4. Подтверждение диалога «Проверка ключевых фраз» (если появился)
5. Кнопка «Показать результаты»
6. Парсинг ленты `#messages_container .feed_item`

## Переменные окружения

См. `apps/api/.env.example`.

## Этапы разработки

1. Маркетинговый сайт (landing, услуги, контакты)
2. API предпросмотра + автоматизация brandanalytics.ru
3. Форма заявки на доступ
4. Telegram-бот и постоянный мониторинг
