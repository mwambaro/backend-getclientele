from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
app = FastAPI(title='Navigation Service')

class NavRequest(BaseModel):
    start: dict
    destinations: List[dict]

@app.post('/navigation')
async def navigation(req: NavRequest):
    # simple straight-line route through destinations
    route = [req.start] + req.destinations
    distance = 0
    for i in range(len(route)-1):
        a = route[i]
        b = route[i+1]
        if a.get('lat') is None or b.get('lat') is None:
            continue
        # naive euclidean in degrees
        distance += ((a['lat']-b['lat'])**2 + (a['lng']-b['lng'])**2)**0.5 * 111000
    return {'route': route, 'distance_m': int(distance)}

@app.get('/forecast')
async def forecast():
    return {'forecast': [{'hour': '09:00', 'expected_visitors': 12}, {'hour': '10:00', 'expected_visitors': 30}]}
