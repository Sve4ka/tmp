from aiogram import types
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
import db.db as db
from api import endpoints
from command import dp
from db.db import add_db
from keyboard import creat_kb as kb

DATA_2 = """
введите данные человека
Оброзование            = {}
Род деятельности       = {}
Награды                = {}
"""


class Q2State(StatesGroup):
    learn = State()
    prof = State()
    prise = State()
    wait = State()


@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('next_q2'), state="*")
async def new_fr(call: types.CallbackQuery, state: FSMContext):
    pp = await endpoints.get_ps_pages(call.message.chat.id)
    print(pp)
    n = int(call.data.split('_')[-1])
    await state.update_data(nn=int(call.data.split('_')[-1]))
    await state.update_data(prof="None")
    await state.update_data(prise="None")
    await state.update_data(learn="None")
    await state.update_data(callback=call)
    await update_keyboard_2(state)

async def update_keyboard_2(state: FSMContext):
    async with state.proxy() as data:
        c = data["learn"]
        m = data["prof"]
        h = data["prise"]
        call = data["callback"]
        if sum([1 if i != "None" else 0 for i in [c, m, h]]) == 3:
            tt = kb.q_kb()
            tt.add(InlineKeyboardButton(text='Все верно', callback_data="pr2_ok"))
            await call.message.edit_text(text="Проверьте введенные данные и, если все "
                                              "верно, нажмите на соответсвующую кнопку \n\n" +
                                              DATA_2.format(c, m, h),
                                         reply_markup=tt)
        else:
            await call.message.edit_text(DATA_2.format(c, m, h), reply_markup=kb.que2())


@dp.callback_query_handler(text='learn_k', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(callback=call)
    await call.message.edit_text("Введите имена детей")
    await Q2State.learn.set()


@dp.callback_query_handler(text='prof_k', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await state.update_data(callback=call)
    await call.message.edit_text("Введите имя супруга/и")
    await Q2State.prof.set()


@dp.callback_query_handler(text='prise_k', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите Гражданство")
    await state.update_data(callback=call)
    await Q2State.prise.set()


@dp.callback_query_handler(text='pr2_ok', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        c = data["learn"]
        m = data["prof"]
        h = data["prise"]
        nn = data["nn"]
        call = data["callback"]
    await state.finish()
    add_db("update dead_table set learn = %s, prof = %s, prise= %s where cr_id=%s", c, m, h, db.search_id_user(call.message.chat.id))
    await call.message.edit_text("Данные сохранены\n\n введите следующие данные",
                                 reply_markup=kb.next_q2(nn))


@dp.message_handler(state=Q2State.learn)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(learn=ph)
    await update_keyboard_2(state)
    await message.delete()
    await state.set_state(Q2State.wait.state)


@dp.message_handler(state=Q2State.prof)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(prof=ph)
    await update_keyboard_2(state)
    await message.delete()
    await state.set_state(Q2State.wait.state)


@dp.message_handler(state=Q2State.prise)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(prise=ph)
    await update_keyboard_2(state)
    await message.delete()
    await state.set_state(Q2State.wait.state)


@dp.message_handler(state=Q2State.wait)
async def wait_state(message: types.Message, state: FSMContext):
    await update_keyboard_2(state)
