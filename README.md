# 🛍 Telegram Digital Store

Telegram Mini App для продажи цифровых товаров за Telegram Stars.

## Архитектура

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Telegram   │────▶│   Bot API   │────▶│   Bot       │
│   Client    │     │  (aiogram)  │     │  (Fly.io)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                                │
                       ┌────────────────────────┘
                       │ SQLite (LiteFS)
                       ▼
┌─────────────┐     ┌─────────────┐
│  Mini App   │◀────│   Vercel    │
│  (Next.js)  │     │  (Frontend) │
└─────────────┘     └─────────────┘
```

## Быстрый старт

### 1. Создай бота
```bash
# Напиши @BotFather
# Получи BOT_TOKEN
# Включи inline mode
# Настрой Telegram Stars в Payments
```

### 2. Клонируй и настрой
```bash
git clone <repo>
cd telegram-digital-store
cp .env.example .env
# Отредактируй .env
```

### 3. Установи зависимости
```bash
pip install -r requirements.txt
```

### 4. Запусти бота
```bash
cd bot
python main.py
```

## Деплой

### Бот → Fly.io (бесплатно)
```bash
flyctl launch --name your-bot-name
flyctl secrets set BOT_TOKEN=your_token
flyctl deploy
```

### Mini App → Vercel (бесплатно)
```bash
cd miniapp
vercel --prod
```

## Монетизация

- **Комиссия 5%** с каждой продажи
- **Pro-подписка** $9.99/мес для креаторов
- **Минимальные затраты** на старте: $0

## Стек

- **Backend:** Python, aiogram 3, FastAPI, SQLAlchemy
- **Frontend:** Next.js, Telegram Mini App SDK
- **DB:** SQLite (LiteFS на Fly.io)
- **Hosting:** Fly.io (bot) + Vercel (miniapp)
- **Payments:** Telegram Stars (0% комиссия интеграции)

## Лицензия

MIT
