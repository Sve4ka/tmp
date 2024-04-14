from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton

from api.endpoints import LoginData, get_access_token
from command import dp
from db.db import add_user, add_db
from keyboard import creat_kb as kb

DATA = """
ВВЕДИТЕ Ваш email и пароль, по которым вы зарегестрированны на memmorycode
email        {}
Пароль       {}
"""


class LoginState(StatesGroup):
    email = State()
    parow = State()
    wait = State()


async def update_keyboard(state: FSMContext):
    async with state.proxy() as data:
        e = data['email']
        parow = data['parow']
        call = data['callback']
        if parow != "None" and e != "None":
            tt = kb.login_kb()
            tt.add(InlineKeyboardButton(text='все верно', callback_data="cr_pr_ok"))
            await call.message.edit_text(text="проверьте введенные данные и если все "
                                              "верно нажмите на соответсвующую кнопку \n\n" +
                                              DATA.format(e, parow),
                                         reply_markup=tt)
        else:
            await call.message.edit_text(DATA.format(e, parow),
                                         reply_markup=kb.login_kb())


@dp.callback_query_handler(text='start', state="*")
async def new_fr(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(email="None")
    await state.update_data(parow="None")
    await state.update_data(callback=call)
    await update_keyboard(state)


@dp.callback_query_handler(text='email', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("введите вашу почту", reply_markup=kb.ret_login_kb())
    await LoginState.email.set()


@dp.callback_query_handler(text='pass', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("введите ваш пароль", reply_markup=kb.ret_login_kb())
    await LoginState.parow.set()


@dp.callback_query_handler(text='ret_login', state='*')
async def new_cancel(call: types.CallbackQuery, state: FSMContext):
    await update_keyboard(state)
    await LoginState.wait.set()


@dp.callback_query_handler(text='cr_pr_ok', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        e = data['email']
        pa = data['parow']
    L = LoginData
    L.email = e
    L.password = pa
    L.device = 'Iphone7'
    add_user(call.message.chat.id, e)
    if await get_access_token(L) == "error":
        await call.message.edit_text(text="неверно введены данные\n"+DATA.format(e, pa),
                                         reply_markup=kb.login_kb())
        add_db("delete from user_table where tg_id=%s", call.message.chat.id)
        await LoginState.wait.set()
        return
    await state.finish()
    await call.message.edit_text("Данные сохранены\n\n", reply_markup=kb.profile())


@dp.message_handler(state=LoginState.email)
async def price_state(message: types.Message, state: FSMContext):
    em = message.text.lower()
    await state.update_data(email=em)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(LoginState.wait.state)


@dp.message_handler(state=LoginState.parow)
async def price_state(message: types.Message, state: FSMContext):
    em = message.text
    await state.update_data(parow=em)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(LoginState.wait.state)


@dp.message_handler(state=LoginState.wait)
async def wait_state(message: types.Message, state: FSMContext):
    await update_keyboard(state)
