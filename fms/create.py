from datetime import datetime
from pprint import pprint
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import InlineKeyboardButton
from api import endpoints
from command import dp, bot
from db.db import add_deader
from keyboard import creat_kb as kb

DATA_CR = """
введите данные человека
Фамилия         = {}
Имя             = {}
Отчество        = {}
Дата рождения   = {}
Дата смерти     = {}
Место рождения  = {}
Место смерти    = {}
"""


class CreatState(StatesGroup):
    name = State()
    surname = State()
    fathname = State()
    birth = State()
    dead = State()
    birth_p = State()
    dead_p = State()
    wait = State()
    photo = State()


async def update_keyboard(state: FSMContext):
    async with state.proxy() as data:
        n = data['name']
        s = data['surname']
        f = data['fathname']
        b = data['birth'].split()[0]
        d = data['dead'].split()[0]
        pb = data['birth_p']
        pd = data['dead_p']
        p = data['photo']
        call = data['callback']
        print(sum([1 if i != "None" else 0 for i in [n, s, f, b, d, p, pb, pd]]))
        if sum([1 if i != "None" else 0 for i in [n, s, f, b, d, p, pb, pd]]) == 8:
            tt = kb.creat_kb()
            tt.add(InlineKeyboardButton(text='Все верно', callback_data="pr_ok"))
            await call.message.edit_text(text="Проверьте введенные данные и, если все "
                                              "верно, нажмите на соответсвующую кнопку \n\n" +
                                              DATA_CR.format(s, n, f, b, d, pb, pd),
                                         reply_markup=tt)
        else:
            if b == "None":
                b = "xx/xx/xxxx"
            if d == "None":
                d = "xx/xx/xxxx"
            await call.message.edit_text(DATA_CR.format(s, n, f, b, d, pb, pd), reply_markup=kb.creat_kb())



@dp.callback_query_handler(lambda callback_query: callback_query.data.startswith('profile_'), state="*")
async def new_fr(call: types.CallbackQuery, state: FSMContext):
    pp = await endpoints.get_ps_pages(call.message.chat.id)
    n = int(call.data.split('_')[-1])
    await state.update_data(nn=int(call.data.split('_')[-1]))
    await state.update_data(name=pp[n]['firstName'])
    await state.update_data(surname=pp[n]['lastName'])
    await state.update_data(fathname=pp[n]["patronym"])
    await state.update_data(birth=pp[n]['birthday_at'])
    await state.update_data(dead=pp[n]['died_at'])
    await state.update_data(birth_p="None")
    await state.update_data(dead_p="None")
    await state.update_data(photo="None")
    await state.update_data(ph_call="None")
    await state.update_data(callback=call)
    await update_keyboard(state)


@dp.callback_query_handler(text='name_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите имя", reply_markup=kb.ret_prof_kb())
    await CreatState.name.set()


@dp.callback_query_handler(text='photo_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Отправьте фото", reply_markup=kb.ret_prof_kb())
    await CreatState.photo.set()


@dp.callback_query_handler(text='surname_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите фамилию", reply_markup=kb.ret_prof_kb())
    await CreatState.surname.set()


@dp.callback_query_handler(text='fathname_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите отчество", reply_markup=kb.ret_prof_kb())
    await CreatState.fathname.set()


@dp.callback_query_handler(text='birth_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите дату рождения, в формате дд/мм/гггг", reply_markup=kb.ret_prof_kb())
    await CreatState.birth.set()


@dp.callback_query_handler(text='dead_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите дату смерти, в формате дд/мм/гггг", reply_markup=kb.ret_prof_kb())
    await CreatState.dead.set()


@dp.callback_query_handler(text='birth_p_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите место рождения", reply_markup=kb.ret_prof_kb())
    await CreatState.birth_p.set()


@dp.callback_query_handler(text='dead_p_cr', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_text("Введите место смерти", reply_markup=kb.ret_prof_kb())
    await CreatState.dead_p.set()


@dp.callback_query_handler(text='ret_prof', state='*')
async def new_cancel(call: types.CallbackQuery, state: FSMContext):
    await update_keyboard(state)
    await CreatState.wait.set()


@dp.callback_query_handler(text='ret_start', state='*')
async def new_cancel(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        p = data['ph_call']
    await state.finish()
    if p != "None":
        await p.delete()
    await call.message.edit_text("Главное меню", reply_markup=kb.profile())



@dp.callback_query_handler(text='pr_ok', state="*")
async def inl_new_fr_name(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        n = data['name']
        s = data['surname']
        f = data['fathname']
        b = data['birth']
        d = data['dead']
        pd = data['dead_p']
        pb = data['birth_p']
        photo = data['photo']
        nn = data['nn']
        p = data['ph_call']
    await state.finish()
    await p.delete()
    b = datetime.strptime(b, '%d/%m/%Y').date()
    d = datetime.strptime(d, '%d/%m/%Y').date()
    add_deader(call.message.chat.id, n, s, f, b, d, pd, pb)
    await call.message.edit_text("Данные сохранены\n\n",
                                 reply_markup=kb.next_q1(nn))


@dp.message_handler(state=CreatState.name)
async def price_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        n = data['name']
        s = data['surname']
        f = data['fathname']
        b = data['birth']
        d = data['dead']
        pd = data['dead_p']
        pb = data['birth_p']
        photo = data['photo']
        nn = data['nn']
        call = data['callback']
    ph = message.text.capitalize()
    await state.update_data(name=ph)
    await update_keyboard(state)

    tmp = await endpoints.put_ps_page(call.message.chat.id, "name", ph, nn, 0)
    pprint(tmp)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.surname)
async def price_state(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        n = data['name']
        s = data['surname']
        f = data['fathname']
        b = data['birth']
        d = data['dead']
        pd = data['dead_p']
        pb = data['birth_p']
        photo = data['photo']
        nn = data['nn']
        call = data['callback']
    ph = message.text.capitalize()
    await state.update_data(surname=ph)
    tmp = await endpoints.put_ps_page(call.message.chat.id, "name", ph, nn, 1)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.fathname)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(fathname=ph)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.birth)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(birth=ph)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.dead)
async def price_state(message: types.Message, state: FSMContext):
    em = message.text
    await state.update_data(dead=em)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)



@dp.message_handler(state=CreatState.birth_p)
async def price_state(message: types.Message, state: FSMContext):
    ph = message.text
    await state.update_data(birth_p=ph)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.dead_p)
async def price_state(message: types.Message, state: FSMContext):
    em = message.text
    await state.update_data(dead_p=em)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)

@dp.message_handler(state=CreatState.photo, content_types=types.ContentType.PHOTO)
async def price_state(message: types.Message, state: FSMContext):
    em = message.photo[-1].file_id
    ph_call = await bot.send_photo(message.chat.id, em)
    await state.update_data(ph_call=ph_call)
    await state.update_data(photo=em)
    await update_keyboard(state)
    await message.delete()
    await state.set_state(CreatState.wait.state)


@dp.message_handler(state=CreatState.photo)
async def price_state(message: types.Message, state: FSMContext):
    await message.delete()


@dp.message_handler(state=CreatState.wait)
async def wait_state(message: types.Message, state: FSMContext):
    await update_keyboard(state)
