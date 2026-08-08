# 🚀 Деплой Telegram Digital Store

## Шаг 1: Подготовка

### 1.1 Создай бота в @BotFather
```
/newbot
→ Введи имя бота
→ Введи username (должен заканчиваться на _bot)
→ Получи BOT_TOKEN — сохрани его
```

### 1.2 Настрой Payments
```
/mybots → Выбери бота → Payments
→ Выбери Telegram Stars
→ Получи подтверждение
```

### 1.3 Включи Inline Mode
```
/mybots → Выбери бота → Inline Mode
→ Turn on
→ Введи placeholder: "Поиск цифровых товаров..."
```

### 1.4 Настрой Mini App
```
/mybots → Выбери бота → Bot Settings → Menu Button
→ Configure menu button
→ Set button text: "🛍 Магазин"
→ Set URL: https://your-miniapp.vercel.app
```

### 1.5 Настрой Domain
```
/mybots → Выбери бота → Bot Settings → Domain
→ Добавь домен: your-miniapp.vercel.app
```

---

## Шаг 2: Деплой бота на Fly.io

### 2.1 Установи flyctl
```bash
curl -L https://fly.io/install.sh | sh
```

### 2.2 Логинься
```bash
flyctl auth login
```

### 2.3 Задеплой
```bash
cd telegram-digital-store

# Создай приложение
flyctl launch --name your-bot-name --no-deploy

# Установи секреты
flyctl secrets set BOT_TOKEN=your_token_here
flyctl secrets set MINI_APP_URL=https://your-miniapp.vercel.app

# Деплой
flyctl deploy
```

### 2.4 Получи URL
```bash
flyctl status
# Скопируй hostname: your-bot-name.fly.dev
```

---

## Шаг 3: Деплой Mini App на Vercel

### 3.1 Установи Vercel CLI
```bash
npm i -g vercel
```

### 3.2 Настрой Mini App
```bash
cd miniapp

# Создай .env.local
echo "NEXT_PUBLIC_API_URL=https://your-bot-name.fly.dev" > .env.local
echo "NEXT_PUBLIC_BOT_USERNAME=your_bot_username" >> .env.local

# Деплой
vercel --prod
```

### 3.3 Получи URL
Vercel выдаст URL типа `https://your-miniapp.vercel.app`

---

## Шаг 4: Свяжи всё вместе

### 4.1 Обнови Mini App URL в боте
```bash
flyctl secrets set MINI_APP_URL=https://your-miniapp.vercel.app
flyctl deploy
```

### 4.2 Обнови URL в @BotFather
```
/mybots → Menu Button → Обнови URL на https://your-miniapp.vercel.app
```

---

## Шаг 5: Тестирование

1. Открой бота → /start
2. Нажми "🚀 Стать креатором"
3. Добавь товар через "➕ Добавить товар"
4. Получи ссылку на магазин
5. Открой ссылку — должен открыться Mini App
6. Нажми "Купить" — должна открыться оплата Stars
7. После оплаты файл придёт в Избранные

---

## 💰 Монетизация

### Комиссия
Платформа берёт 5% с каждой продажи. Настройка в `.env`:
```
COMMISSION_PERCENT=5.0
```

### Pro-подписка (вручную)
Пока креаторы пишут админу для апгрейда. Автоматизация — в следующей версии.

### Вывод Stars
1. Креатор накапливает 1000+ Stars
2. Пишет админу
3. Админ переводит Stars через Fragment

---

## 📊 Мониторинг

### Логи бота
```bash
flyctl logs
```

### Статус
```bash
flyctl status
```

### База данных
SQLite хранится в контейнере. Для бэкапа:
```bash
flyctl ssh sftp get /app/bot/store.db ./backup.db
```

---

## 🔄 Обновление

```bash
# Внеси изменения в код
git add .
git commit -m "update"

# Передеплой
flyctl deploy
vercel --prod
```

---

## 🆘 Траблшутинг

### Бот не отвечает
```bash
flyctl logs
# Проверь BOT_TOKEN
```

### Mini App не открывается
- Проверь, что домен добавлен в @BotFather
- Проверь CORS в api.py
- Проверь URL в .env.local

### Оплата не проходит
- Убедись, что Stars включены в @BotFather
- Проверь, что цена > 0
- Проверь логи: `flyctl logs`

### Файл не отправляется
- Проверь, что file_id сохранился в БД
- Проверь, что бот имеет доступ к файлу (не удаляйте файл из чата)
