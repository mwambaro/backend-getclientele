from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="AI Intent Service")

class IntentRequest(BaseModel):
    text: str
    language: Optional[str] = 'en'


@app.post('/intent')
async def detect_intent(req: IntentRequest):
    text = req.text.lower()
    intent = {'category': 'general', 'price': 'medium', 'audience': None}
    if 'cheap' in text or 'low' in text:
        intent['price'] = 'low'
    if 'kids' in text or 'children' in text:
        intent['audience'] = 'kids'
    if 'shoe' in text or 'shoes' in text:
        intent['category'] = 'shoes'
    return {'text': req.text, 'intent': intent}


@app.post('/categorize')
async def categorize(req: IntentRequest):
    text = req.text.lower()
    cats = ['general']
    if 'shoe' in text:
        cats = ['shoes']
    if 'food' in text or 'tomato' in text or 'eggs' in text:
        cats = ['groceries']
    return {'categories': cats}
