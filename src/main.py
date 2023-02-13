from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import redis
from datetime import date
from uuid import uuid4

app = FastAPI()
templates = Jinja2Templates(directory="src/templates")
USERS_KEY = 'users'
DAYS_KEY = 'dates'

r = redis.Redis(host="redis", port=6379, decode_responses=True)


def all_users():
    return list(sorted(r.hgetall(USERS_KEY).keys()))


def add_date():
    if today() not in r.lrange(DAYS_KEY, 0, -1):
        r.rpush(DAYS_KEY, today())


def today():
    return date.today().isoformat()


@app.get("/")
def read_root(request: Request):
    users = all_users()
    add_date()
    return templates.TemplateResponse('home.html', context={'request': request, 'added_users': users})


@app.get("/add")
def add_user(request: Request):
    return templates.TemplateResponse('add_user.html', context={'request': request})


@app.post("/add")
def added_user(request: Request, name: str = Form(...)):
    r.hset(USERS_KEY, name, str(uuid4()))
    return templates.TemplateResponse('added_user.html', context={'request': request, 'added': name})


@app.get("/select_user")
def select_user_for_notes(request: Request):
    users = all_users()
    return templates.TemplateResponse('select_for_note.html', context={'request': request, 'added_users': users})


@app.get("/take_note")
def take_notes_for_user(request: Request, name: str = ''):
    user_id = r.hget(USERS_KEY, name)
    notes = r.hget(user_id, today())
    if not notes:
        notes = ''
    return templates.TemplateResponse('take_note.html', context={'request': request, 'name': name, 'notes': notes})


@app.post("/take_note")
def see_notes_for_user(request: Request, name: str = '', notes: str = Form(...)):
    user_id = r.hget(USERS_KEY, name)
    r.hset(user_id, today(), notes)
    return templates.TemplateResponse('taken_notes.html', context={'request': request, 'name': name, 'notes': notes})


@app.get("/select_day")
def see_notes(request: Request):
    return templates.TemplateResponse('select_day.html', context={'request': request, 'days': r.lrange(DAYS_KEY, 0, -1)})


@app.get("/days_notes")
def see_notes(request: Request, date: str = ''):
    users = r.hgetall(USERS_KEY)
    data = {}
    for name, user_id in users.items():
        data[name] = r.hget(user_id, date)

    return templates.TemplateResponse('days_notes.html', context={'request': request, 'day': date, 'notes': data})


@app.get("/test")
def test():
    return {'dates': r.lrange('dates', 0, -1)}

# @app.get('/clear')
# def clear_users():
#     r.delete(USERS_KEY)
#     return RedirectResponse('/', status_code=303)
