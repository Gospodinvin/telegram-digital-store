import logging
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, SuccessfulPayment, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy.orm import Session
from datetime import datetime

from config import settings
from models import Creator, Product, Purchase, init_db
from states import AddProduct
from keyboards import (
    main_menu_kb, add_product_confirm_kb, product_actions_kb,
    payment_kb, back_to_menu_kb, miniapp_store_link
)

router = Router()
logger = logging.getLogger(__name__)

SessionLocal = init_db(settings.DATABASE_URL)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

def get_or_create_creator(db: Session, user) -> Creator:
    creator = db.query(Creator).filter(Creator.telegram_id == user.id).first()
    if not creator:
        creator = Creator(
            telegram_id=user.id,
            username=user.username,
            first_name=user.first_name
        )
        db.add(creator)
        db.commit()
        db.refresh(creator)
    return creator

def format_product_card(product: Product) -> str:
    lines = [
        f"📦 <b>{product.name}</b>",
        f"💰 <b>Цена:</b> {product.price_stars} Stars",
        f"📊 <b>Продаж:</b> {product.sales_count}",
        f"📝 {product.description or 'Без описания'}"
    ]
    return "\n".join(lines)

# ========== START & MENU ==========

@router.message(CommandStart())
async def cmd_start(message: Message):
    db = get_db()
    creator = get_or_create_creator(db, message.from_user)

    welcome_lines = [
        f"👋 Привет, {message.from_user.first_name}!",
        "",
        "🛍 <b>Telegram Digital Store</b> — продавай цифровые товары прямо в Telegram.",
        "",
        "<b>Как это работает:</b>",
        "1️⃣ Загрузи свой товар (PDF, видео, шаблоны)",
        "2️⃣ Установи цену в Stars",
        "3️⃣ Получи ссылку на магазин",
        "4️⃣ Покупатели платят — деньги приходят тебе",
        "",
        f"<b>Комиссия платформы:</b> {settings.COMMISSION_PERCENT}%"
    ]
    welcome_text = "\n".join(welcome_lines)

    await message.answer(welcome_text, reply_markup=main_menu_kb(bool(creator)))

@router.callback_query(F.data == "main_menu")
async def back_to_menu(callback: CallbackQuery):
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()
    await callback.message.edit_text("🏠 Главное меню", reply_markup=main_menu_kb(bool(creator)))
    await callback.answer()

# ========== BECOME CREATOR ==========

@router.callback_query(F.data == "become_creator")
async def become_creator(callback: CallbackQuery):
    db = get_db()
    creator = get_or_create_creator(db, callback.from_user)
    await callback.message.edit_text(
        "✅ Ты зарегистрирован как креатор! Теперь можешь добавлять товары.",
        reply_markup=main_menu_kb(True)
    )
    await callback.answer()

# ========== ADD PRODUCT (FSM) ==========

@router.callback_query(F.data == "add_product")
async def add_product_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AddProduct.name)
    await callback.message.edit_text(
        "📝 <b>Шаг 1/4</b>\nВведи название товара:",
        reply_markup=back_to_menu_kb()
    )
    await callback.answer()

@router.message(AddProduct.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AddProduct.description)
    await message.answer(
        "📝 <b>Шаг 2/4</b>\nВведи описание товара (или отправь /skip):",
        reply_markup=back_to_menu_kb()
    )

@router.message(AddProduct.description)
async def process_description(message: Message, state: FSMContext):
    desc = message.text if message.text != "/skip" else ""
    await state.update_data(description=desc)
    await state.set_state(AddProduct.price)
    await message.answer(
        "💎 <b>Шаг 3/4</b>\nВведи цену в Telegram Stars (минимум 1):",
        reply_markup=back_to_menu_kb()
    )

@router.message(AddProduct.price)
async def process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        if price < 1:
            raise ValueError
        await state.update_data(price=price)
        await state.set_state(AddProduct.file)
        await message.answer(
            "📎 <b>Шаг 4/4</b>\nОтправь файл товара (документ, фото, видео, аудио):",
            reply_markup=back_to_menu_kb()
        )
    except ValueError:
        await message.answer("❌ Введи целое число больше 0.")

@router.message(AddProduct.file, F.content_type.in_({"document", "photo", "video", "audio"}))
async def process_file(message: Message, state: FSMContext):
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        file_size = message.document.file_size
    elif message.photo:
        file_id = message.photo[-1].file_id
        file_name = "photo.jpg"
        file_size = message.photo[-1].file_size
    elif message.video:
        file_id = message.video.file_id
        file_name = message.video.file_name or "video.mp4"
        file_size = message.video.file_size
    elif message.audio:
        file_id = message.audio.file_id
        file_name = message.audio.file_name or "audio.mp3"
        file_size = message.audio.file_size
    else:
        await message.answer("❌ Неподдерживаемый тип файла.")
        return

    await state.update_data(file_id=file_id, file_name=file_name, file_size=file_size)
    data = await state.get_data()

    preview_lines = [
        "📋 <b>Проверь данные:</b>",
        "",
        f"📦 <b>Название:</b> {data['name']}",
        f"📝 <b>Описание:</b> {data.get('description', 'Нет')}",
        f"💎 <b>Цена:</b> {data['price']} Stars",
        f"📎 <b>Файл:</b> {file_name}",
        "",
        "Всё верно?"
    ]
    preview = "\n".join(preview_lines)

    await state.set_state(AddProduct.confirm)
    await message.answer(preview, reply_markup=add_product_confirm_kb())

@router.callback_query(AddProduct.confirm, F.data == "confirm_product")
async def confirm_product(callback: CallbackQuery, state: FSMContext):
    db = get_db()
    data = await state.get_data()

    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()

    product = Product(
        creator_id=creator.id,
        name=data["name"],
        description=data.get("description", ""),
        price_stars=data["price"],
        file_id=data["file_id"],
        file_name=data.get("file_name", ""),
        file_size=data.get("file_size", 0)
    )
    db.add(product)
    db.commit()
    db.refresh(product)

    store_url = f"{settings.MINI_APP_URL}?creator={creator.telegram_id}"

    text_lines = [
        "✅ <b>Товар опубликован!</b>",
        "",
        f"🔗 <b>Ссылка на магазин:</b>\n{store_url}",
        "",
        "Отправь её подписчикам — они смогут купить товар прямо в Telegram."
    ]

    await callback.message.edit_text(
        "\n".join(text_lines),
        reply_markup=miniapp_store_link(store_url)
    )
    await state.clear()
    await callback.answer()

@router.callback_query(AddProduct.confirm, F.data == "cancel_product")
async def cancel_product(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()
    await callback.message.edit_text("❌ Добавление отменено.", reply_markup=main_menu_kb(bool(creator)))
    await callback.answer()

# ========== MY PRODUCTS ==========

@router.callback_query(F.data == "my_products")
async def my_products(callback: CallbackQuery):
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()
    products = db.query(Product).filter(Product.creator_id == creator.id, Product.is_active == True).all()

    if not products:
        await callback.message.edit_text(
            "📭 У тебя пока нет товаров.\n\nДобавь первый!",
            reply_markup=main_menu_kb(True)
        )
        await callback.answer()
        return

    lines = ["📦 <b>Твои товары:</b>\n"]
    for p in products:
        lines.append(f"• {p.name} — {p.price_stars} Stars (продаж: {p.sales_count})")

    await callback.message.edit_text("\n".join(lines), reply_markup=main_menu_kb(True))
    await callback.answer()

# ========== STATS ==========

@router.callback_query(F.data == "stats")
async def stats(callback: CallbackQuery):
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()
    products = db.query(Product).filter(Product.creator_id == creator.id).all()

    total_sales = sum(p.sales_count for p in products)
    total_earned = db.query(Purchase).filter(
        Purchase.product_id.in_([p.id for p in products]),
        Purchase.status == "completed"
    ).all()
    earned = sum(p.creator_earned for p in total_earned)

    lines = [
        "📊 <b>Статистика:</b>",
        "",
        f"📦 Товаров: {len(products)}",
        f"💰 Продаж: {total_sales}",
        f"⭐ Заработано: {earned} Stars",
        f"💎 Баланс: {creator.balance_stars} Stars"
    ]

    await callback.message.edit_text("\n".join(lines), reply_markup=main_menu_kb(True))
    await callback.answer()

# ========== BALANCE ==========

@router.callback_query(F.data == "balance")
async def balance(callback: CallbackQuery):
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()

    lines = [
        "💰 <b>Твой баланс:</b>",
        "",
        f"⭐ Доступно: {creator.balance_stars} Stars",
        "",
        "<b>Как вывести:</b>",
        "1. Перейди в @BotFather → Bot Settings → Payments",
        "2. Выбери Telegram Stars → Transfer",
        "3. Укажи свой кошелёк TON",
        "",
        "Минимум для вывода: 1000 Stars (~$13)"
    ]

    await callback.message.edit_text("\n".join(lines), reply_markup=main_menu_kb(True))
    await callback.answer()

# ========== MY STORE ==========

@router.callback_query(F.data == "my_store")
async def my_store(callback: CallbackQuery):
    db = get_db()
    creator = db.query(Creator).filter(Creator.telegram_id == callback.from_user.id).first()
    store_url = f"{settings.MINI_APP_URL}?creator={creator.telegram_id}"

    await callback.message.edit_text(
        f"🛍 <b>Твой магазин:</b>\n\n{store_url}\n\nПоделись этой ссылкой в своём канале или соцсетях!",
        reply_markup=miniapp_store_link(store_url)
    )
    await callback.answer()

# ========== INLINE MODE ==========

@router.inline_query()
async def inline_search(inline_query: InlineQuery):
    db = get_db()
    query = inline_query.query.strip()

    if not query:
        products = db.query(Product).filter(Product.is_active == True).order_by(Product.sales_count.desc()).limit(10).all()
    else:
        products = db.query(Product).filter(
            Product.is_active == True,
            Product.name.ilike(f"%{query}%")
        ).limit(10).all()

    results = []
    for p in products:
        store_url = f"{settings.MINI_APP_URL}?product={p.id}"
        results.append(
            InlineQueryResultArticle(
                id=str(p.id),
                title=f"{p.name} — {p.price_stars} Stars",
                description=p.description or "Цифровой товар",
                input_message_content=InputTextMessageContent(
                    message_text=f"🛍 <b>{p.name}</b>\n💰 {p.price_stars} Stars\n\n{store_url}"
                ),
                reply_markup=miniapp_store_link(store_url)
            )
        )

    await inline_query.answer(results, cache_time=1)

# ========== BUY ==========

@router.callback_query(F.data.startswith("buy_"))
async def buy_product(callback: CallbackQuery):
    parts = callback.data.split("_")
    product_id = int(parts[1])

    db = get_db()
    product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()

    if not product:
        await callback.answer("❌ Товар не найден.", show_alert=True)
        return

    if product.creator.telegram_id == callback.from_user.id:
        await callback.answer("❌ Это твой товар!", show_alert=True)
        return

    await callback.message.edit_text(
        format_product_card(product),
        reply_markup=payment_kb(product.id, product.price_stars)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("pay_"))
async def process_payment(callback: CallbackQuery, bot: Bot):
    parts = callback.data.split("_")
    product_id = int(parts[1])
    price = int(parts[2])

    db = get_db()
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        await callback.answer("❌ Товар не найден.", show_alert=True)
        return

    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title=product.name,
        description=product.description or "Цифровой товар",
        payload=f"product_{product_id}_{callback.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[{"label": product.name, "amount": price}]
    )
    await callback.answer()

@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    payment = message.successful_payment
    payload = payment.invoice_payload

    parts = payload.split("_")
    product_id = int(parts[1])
    buyer_id = int(parts[2])

    db = get_db()
    product = db.query(Product).filter(Product.id == product_id).first()
    creator = product.creator

    commission = int(payment.total_amount * settings.COMMISSION_PERCENT / 100)
    creator_earned = payment.total_amount - commission

    purchase = Purchase(
        product_id=product_id,
        buyer_telegram_id=buyer_id,
        buyer_username=message.from_user.username,
        price_paid=payment.total_amount,
        commission=commission,
        creator_earned=creator_earned,
        telegram_payment_id=payment.telegram_payment_charge_id
    )
    db.add(purchase)

    creator.balance_stars += creator_earned
    product.sales_count += 1
    db.commit()

    await bot.send_document(
        chat_id=buyer_id,
        document=product.file_id,
        caption=f"✅ <b>Спасибо за покупку!</b>\n\n📦 {product.name}\n💰 Оплачено: {payment.total_amount} Stars\n\nСохрани этот файл — он отправлен в твои Избранные."
    )

    await bot.send_message(
        chat_id=creator.telegram_id,
        text=f"🎉 <b>Новая продажа!</b>\n\n📦 {product.name}\n💰 +{creator_earned} Stars (комиссия {commission} Stars)\n💎 Баланс: {creator.balance_stars} Stars"
    )

    await message.answer("✅ Оплата прошла успешно! Файл отправлен в твои Избранные.")

# ========== DELETE ==========

@router.callback_query(F.data.startswith("delete_"))
async def delete_product(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    db = get_db()
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product or product.creator.telegram_id != callback.from_user.id:
        await callback.answer("❌ Нет доступа.", show_alert=True)
        return

    product.is_active = False
    db.commit()

    await callback.message.edit_text("🗑 Товар удалён.", reply_markup=main_menu_kb(True))
    await callback.answer()

# ========== HELP ==========

@router.callback_query(F.data == "help")
async def help_cmd(callback: CallbackQuery):
    lines = [
        "❓ <b>Помощь</b>",
        "",
        "<b>Для креаторов:</b>",
        "• Добавляй товары через «➕ Добавить товар»",
        "• Устанавливай цену в Telegram Stars",
        "• Делись ссылкой на магазин",
        "• Получай оплату мгновенно",
        "",
        "<b>Для покупателей:</b>",
        "• Найди товар через поиск",
        "• Оплати Stars (покупаются в Settings → Stars)",
        "• Получи файл мгновенно",
        "",
        "<b>Поддержка:</b> @your_support"
    ]

    await callback.message.edit_text("\n".join(lines), reply_markup=back_to_menu_kb())
    await callback.answer()
