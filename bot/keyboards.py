from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder

def main_menu_kb(is_creator: bool = False):
    builder = InlineKeyboardBuilder()
    if is_creator:
        builder.button(text="📦 Мои товары", callback_data="my_products")
        builder.button(text="➕ Добавить товар", callback_data="add_product")
        builder.button(text="📊 Статистика", callback_data="stats")
        builder.button(text="💰 Баланс", callback_data="balance")
        builder.button(text="🛒 Мой магазин", callback_data="my_store")
    else:
        builder.button(text="🚀 Стать креатором", callback_data="become_creator")
        builder.button(text="🛒 Найти товары", callback_data="browse_store")
    builder.button(text="❓ Помощь", callback_data="help")
    builder.adjust(2)
    return builder.as_markup()

def add_product_confirm_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="✅ Опубликовать", callback_data="confirm_product")
    builder.button(text="❌ Отмена", callback_data="cancel_product")
    return builder.as_markup()

def product_actions_kb(product_id: int, is_owner: bool = False):
    builder = InlineKeyboardBuilder()
    builder.button(text="💳 Купить", callback_data=f"buy_{product_id}")
    if is_owner:
        builder.button(text="🗑 Удалить", callback_data=f"delete_{product_id}")
    builder.adjust(2)
    return builder.as_markup()

def payment_kb(product_id: int, price: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=f"💎 Заплатить {price} Stars",
        callback_data=f"pay_{product_id}_{price}"
    )
    builder.button(text="❌ Отмена", callback_data="cancel_payment")
    return builder.as_markup()

def back_to_menu_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="◀️ В меню", callback_data="main_menu")
    return builder.as_markup()

def miniapp_store_link(url: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url=url))]
    ])
