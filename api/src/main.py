from fastapi import FastAPI, Form, Request
import redis
from datetime import date, timedelta
from uuid import uuid4
from random import random
from src.models.add_user import AddUserModel
from src.models.update_notes import UpdateNotesModel

app = FastAPI()


USERS_KEY = 'users'
DAYS_KEY = 'dates'
REORDERED_USERS = 'randomized'

r = redis.Redis(host="redis", port=6379, decode_responses=True)


def has_random():
    return not not r.lrange(REORDERED_USERS, 0, -1)


def all_users():
    ordered_users = r.lrange(REORDERED_USERS, 0, -1)
    if ordered_users:
        return ordered_users
    return list(sorted(r.hgetall(USERS_KEY).keys()))


@app.get("/users")
def read_root():
    return all_users()


@app.post("/add")
def add_user(user: AddUserModel):
    try:
        had_random = has_random()
        clear_randomize_users()

        r.hset(USERS_KEY, user.name, str(uuid4()))
        if had_random:
            randomize_users()
    except Exception as e:
        return False
    else:
        return True


@app.post("/randomize")
def randomize_users(order: str = ''):
    try:
        order_list = order.split(',')

        users = all_users()
        users = list(sorted(users, key=lambda x: .5 - random()))

        r.delete(REORDERED_USERS)
        r.rpush(REORDERED_USERS, *users)
    except Exception as e:
        return False
    else:
        return True


@app.post('/clear_randomize')
def clear_randomize_users():
    r.delete(REORDERED_USERS)
    return True


@app.get("/get_range")
def get_day_notes(start: str = "", end: str = "", single: str = "", includeBlanks: bool = False):

    if single:
        start = single
        end = single

    if start > end:
        start, end = end, start
    start_date = date.fromisoformat(start)
    end_date = date.fromisoformat(end)

    # make sure range will trigger end date
    range_delta = end_date - start_date
    range_delta = range_delta + timedelta(days=1)

    users = r.hgetall(USERS_KEY)
    data = {}
    for name, user_id in users.items():
        user_notes = r.hgetall(user_id)
        for delta in range(range_delta.days):
            date_iso = (start_date + timedelta(days=delta)).isoformat()

            days_info = data.get(date_iso, {})
            user_note = user_notes.get(date_iso, None)
            if user_note or includeBlanks:
                days_info[name] = user_note
                data[date_iso] = days_info

    return data


@app.get("/user_notes")
def get_notes_for_user(userName: str = "", date: str = ""):
    if not date:
        return ''

    user_id = r.hget(USERS_KEY, userName)

    if not user_id:
        return ''

    user_note = r.hget(user_id, date)

    if not user_note:
        user_note = ''

    return user_note


@app.post("/user_notes")
def set_notes_for_user(user_data: UpdateNotesModel):
    if not user_data.date:
        return False

    user_id = r.hget(USERS_KEY, user_data.name)

    if not user_id:
        return False

    r.hset(user_id, user_data.date, user_data.note)
    return True


@app.get("/dates")
def get_dates():
    users = r.hgetall(USERS_KEY)
    dates = []
    for _, user_id in users.items():
        user_data = r.hgetall(user_id)
        dates = list(user_data.keys()) + dates

    dates = list(sorted(list(set(dates))))

    return dates
