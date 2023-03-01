from fastapi import FastAPI, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import date
from uuid import uuid4
from random import random
from json import dumps
import requests

app = FastAPI()

api_layer = 'http://api/'


app.mount("/src/static", StaticFiles(directory="src/static"), name="static")
templates = Jinja2Templates(directory="src/templates")


def get(endpoint: str):
    return requests.get(f'{api_layer}{endpoint}')

def post(endpoint: str, payload: dict = {}):
    print(payload)
    return requests.post(f'{api_layer}{endpoint}', data=dumps(payload))


def all_users():
    req = get('users')
    if req.status_code == 200:
        return req.json()


def today():
    return date.today().isoformat()


@app.get("/")
def read_root(request: Request):
    users = all_users()
    return templates.TemplateResponse('home.html', context={'request': request, 'added_users': users})


@app.get("/add")
def add_user(request: Request, added: str = '', succeed: bool = True):
    if not succeed:
        print('oops')
    return templates.TemplateResponse('add_user.html', context={'request': request, 'added': added})


@app.post("/add")
def added_user(request: Request, name: str = Form(...)):
    req = post("add", {"name": name})
    if req.status_code == 200:
        return RedirectResponse(f'/add?added={name}&succeed=True', status_code=303)
    else:
        return req.json()

@app.get("/select_user")
def select_user_for_notes(request: Request):
    users = all_users()
    return templates.TemplateResponse('select_for_note.html', context={'request': request, 'added_users': users})


@app.get("/take_note")
def take_notes_for_user(request: Request, name: str = '', date: str = ''):
    notes = get(f'user_notes?userName={name}&date={date}').json()

    return templates.TemplateResponse('take_note.html', context={'request': request, 'name': name, 'notes': notes})


@app.post("/take_note")
def see_notes_for_user(request: Request, name: str = '', notes: str = Form(...), date: str = Form(...)):
    post('user_notes', {
        "name": name,
        "date": date,
        "note": notes
    })
    return templates.TemplateResponse('taken_notes.html', context={'request': request, 'name': name, 'notes': notes})


@app.get("/select_day")
def see_notes(request: Request):
    days = get('dates').json()
    print(f'{days=}')
    return templates.TemplateResponse('select_day.html', context={'request': request, 'days': days})


@app.get("/days_notes")
def see_notes(request: Request, date: str = ''):
    data = get(f'get_range?single={date}').json()
    notes = {}

    if data[date]:
        notes = data[date]

    return templates.TemplateResponse('days_notes.html', context={'request': request, 'day': date, 'notes': notes})


@app.get('/randomize')
def randomize_users(request: Request, order: str = ''):
    post('randomize')
    return RedirectResponse('/', status_code=303)


@app.get('/clear_randomize')
def clear_randomize_users():
    post('clear_randomize')
    return RedirectResponse('/', status_code=303)
