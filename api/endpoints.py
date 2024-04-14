import httpx
from pydantic import BaseModel

import db.db as db

link = [60482012, 43724180]


class LoginData(BaseModel):
    email: str
    password: str
    device: str


async def get_access_token(login_data: LoginData):
    url = "https://mc.dev.rand.agency/api/v1/get-access-token/"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8"
    }
    data = {
        'email': login_data.email,
        'password': login_data.password,
        'device': login_data.device
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        if response.status_code != 200:
            return "error"
        access_token = response.json()['access_token']
        print(access_token)
        db.add_db("UPDATE user_table SET token=%s WHERE id=%s",
                  access_token, db.search_id_user_by_email(data["email"]))
        return "true"


async def get_ps_pages(tg_id):
    print("get_ps_pages")
    token = db.answer_bd("select token from user_table where tg_id = %s", tg_id)[0][0]
    url = "https://mc.dev.rand.agency/api/page/60482012"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        if resp.status_code != 200:
            return resp.status_code
    url = "https://mc.dev.rand.agency/api/page/43724180"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {token}"
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code != 200:
            return response.status_code

    return [resp.json(), response.json()]


async def put_ps_page(tg_id, key, new_data, n, i):
    token = db.answer_bd("select token from user_table where tg_id = %s", tg_id)[0][0]
    url = f"https://mc.dev.rand.agency/api/page/{link[n]}"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json;charset=UTF-8",
        "Authorization": f"Bearer {token}"  # Предполагаем, что токен передается в формате Bearer
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(type(data))
            print(key, new_data, data.get(key, 'Key not found'))
            tt = data[key].split()
            try:
                tt[i] = new_data
            except:
                tt.append(new_data)
            data[key] = ' '.join(tt)
            # Обновляем данные
            # pprint.pprint(data)
            res2 = await client.put(url, headers=headers, json=data)  # Используем параметр json для отправки словаря
            if res2.status_code == 200:
                print(res2.json()[key])
                print(type(res2.json()))
                return res2.json()  # Возвращаем обновленные данные
            else:
                return f"Error updating page: {res2.status_code}"  # Возвращаем код ошибки при попытке обновления
        else:
            return f"Error fetching page: {response.status_code}"  # Возвращаем код ошибки при попытке получения данных

# Пример использования (замените db на вашу реализацию базы данных)
# asyncio.run(put_ps_page('your_tg_id', 'your_key', 'your_new_data', 0))
