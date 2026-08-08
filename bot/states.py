from aiogram.fsm.state import State, StatesGroup

class AddProduct(StatesGroup):
    name = State()
    description = State()
    price = State()
    file = State()
    confirm = State()
