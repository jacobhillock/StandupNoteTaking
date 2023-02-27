from fastapi import FastAPI, Form, Request
import redis
from datetime import date
from uuid import uuid4
from random import random
from src.models.add_user import AddUserModel

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

@app.get("/get_days")
def get_day_notes(date: str = ''):
    users = r.hgetall(USERS_KEY)
    data = {}
    for name, user_id in users.items():
        data[name] = r.hget(user_id, date)
    
    return data


@app.get("/dates")
def get_dates():
    users = r.hgetall(USERS_KEY)
    dates = []
    for _, user_id in users.items():
        user_data = r.hgetall(user_id)
        dates = list(user_data.keys()) + dates
    
    dates = list(set(dates))

    return dates
