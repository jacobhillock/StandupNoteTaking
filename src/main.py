from fastapi import FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
import redis

app = FastAPI()
templates = Jinja2Templates(directory="/code/src/templates")

r = redis.Redis(host="redis", port=6379)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get('/hits')
def read_root():
    r.incr('hits')
    return {"number of hits": r.get("hits")}

@app.get("/add")
def form_post(request: Request):
    return templates.TemplateResponse('add_user.html', context={'request': request})

@app.post("/add")
def form_post(request: Request, name: str = Form(...)):
    return templates.TemplateResponse('added_user.html', context={'request': request, 'added': name})