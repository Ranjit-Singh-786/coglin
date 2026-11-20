from contextlib import asynccontextmanager
import re

import joblib
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from emaildata import init_db, insert_prediction


# Load the model and CountVectorizer.
model = joblib.load('models/multinomialnaivebayes.lb')
bow_obj = joblib.load('models/countvectorizer.lb')
templates = Jinja2Templates(directory='templates')


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Email Classification",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get('/', response_class=HTMLResponse, name='home')
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='home.html',
        context={},
    )


@app.post('/prediction', response_class=HTMLResponse, name='prediction')
async def prediction(request: Request, emailContent: str = Form(...)):
    original_content = emailContent.strip()
    if not original_content:
        return templates.TemplateResponse(
            request=request,
            name='home.html',
            context={'error': 'Please enter a message to classify.'},
            status_code=400,
        )

    # Keep the submitted text intact in the database; preprocess only for the model.
    model_input = re.sub(r'[^a-zA-Z ]', '', original_content.lower())
    transformed_input = bow_obj.transform([model_input])
    prediction_label = model.predict(transformed_input)[0]
    result = {'1': 'SPAM', '0': 'HAM'}.get(str(prediction_label), 'HAM')

    insert_prediction(original_content, result)
    return templates.TemplateResponse(
        request=request,
        name='home.html',
        context={'output': result, 'submitted_text': original_content},
    )
