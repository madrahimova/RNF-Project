import sys
import json

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

sys.path.append('.')
from app.core.core import *

app = FastAPI()


# Тестовая ручка
@app.get("/", response_class=HTMLResponse)
async def test():
    return "OK"


# Получить все анкеты
@app.get("/form/all")
async def get_all_forms():
    data = state.get("df").to_json(orient="records", force_ascii=False)
    return {"data": json.loads(data)}


# Получить анкеты c номерами [start, start + n]
# Нужно для пагинации
# NOTE: нумерация идет с 0, но в ответе анкеты с 1
@app.get("/form/batch")
async def get_form_batch(start: int, n: int):
    if n < 0:
        raise HTTPException(status_code=400)
    df = state.get("df")
    end = start + n
    if start < 0 or end > len(df):
        raise HTTPException(status_code=400)
    data = df.iloc[start:end]
    if len(data) == 0:
        raise HTTPException(status_code=404)
    data = data.to_json(orient="records", force_ascii=False)
    return {"data": json.loads(data)}


# Получить анкету по номеру
@app.get("/form/{no}")
async def get_form_by_no(no: int):
    if no < 1:
        raise HTTPException(status_code=400)
    df = state.get("df")
    data = df[df["no"] == no]
    if len(data) == 0:
        raise HTTPException(status_code=404)
    data = data.to_json(orient="records", force_ascii=False)
    return {"data": json.loads(data)}


# Фильтровать анкеты по полу
@app.get("/filter/gender")
async def filter_by_gender(men: bool):
    men_woman_df = get_men_woman_df()
    df = None
    if men:
        df = men_woman_df["men_df"]
    else:
        df = men_woman_df["woman_df"]
    if df is None or len(df) == 0:
        raise HTTPException(status_code=404)
    data = df.to_json(orient="records", force_ascii=False)
    return {"data": json.loads(data)}


# Фильтровать анкеты по полу с пагинацией
@app.get("/filter/gender/batch")
async def filter_batch_by_gender(men: bool, start: int, n: int):
    if n < 0:
        raise HTTPException(status_code=400)
    df = None
    try:
        men_woman_df = state.get("men_woman_df")
    except:
        men_woman_df = get_men_woman_df()
        state.set("men_woman_df", men_woman_df)
    if men:
        df = men_woman_df["men_df"]
    else:
        df = men_woman_df["woman_df"]
    end = start + n
    if start < 0 or end > len(df):
        raise HTTPException(status_code=400)
    data = df.iloc[start:end]
    if len(data) == 0:
        raise HTTPException(status_code=404)
    data = data.to_json(orient="records", force_ascii=False)
    return {"data": json.loads(data)}


# Рассчитать статистику по мужчинам и женщинам
@app.get("/stat/gender")
async def stat_by_gender():
    try:
        state.get("men_woman_df")
    except:
        state.set("men_woman_df", get_men_woman_df())
    return {"data": stat_men_women()}


if __name__ == "__main__":
    df = get_df()
    state.set("df", df)
    city_df = get_city_df()
    state.set("city_df", city_df)
    capital_df = get_capital_df(city_df)
    state.set("capital_df", capital_df)
    name_df = get_name_df()
    state.set("name_df", name_df)
    uvicorn.run(app, host="0.0.0.0", port=8000)
