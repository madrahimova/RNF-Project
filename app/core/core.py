import threading

import pandas as pd
import re
import os
import numpy as np
from app.models.models import *

DATA_PATH = "/opt/rnf/data"

if os.getenv("LOCAL_RUN"):
    DATA_PATH = "app/core/data"

DS_PATH = f"{DATA_PATH}/dataset.xlsx"
CITY_DS_PATH = f"{DATA_PATH}/worldcities.xlsx"
NAME_DS_PATH = f"{DATA_PATH}/names.jsonl"


# Загрузить основной датафрейм с полями
# no - номер анкеты
# name - полное имя
# life_years - годы жизни
# grad_year - год выпуска из ВУЗа
# faculty - факультет/отделение ВУЗа
# university - название ВУЗа
# rus_cv - деятельность в России
# fc_cv - деятельность за рубежом
# type - нисходящая/стабильная/восходящая карьера, далее - Н/С/В
# place - место проживания за рубежом
def get_df():
    df = pd.read_excel(DS_PATH, header=None, names=["no", "name", "life_years",
                                                    "grad_year", "faculty", "university",
                                                    "rus_cv", "fc_cv", "type", "place"], skiprows=1)
    return df


# Загрузить вспомогательный датафрейм с данными городов
# Нужно для определения, является ли ВУЗ столичным
def get_city_df():
    city_df = pd.read_excel(CITY_DS_PATH)
    return city_df


# Получить датафрейм столиц
def get_capital_df(city_df):
    capital_df = pd.DataFrame(columns=["city"])
    for row in city_df.to_dict(orient="records"):
        if row["capital"] == "primary":
            capital_df.loc[-1] = {"city": row["city"].lower()}
            capital_df.index = capital_df.index + 1
    return capital_df


# Загрузить датафрейм с данными имен
# Нужно для определения пола респондента
def get_name_df():
    name_df = pd.read_json(NAME_DS_PATH, lines=True)
    return name_df


# Получить и обработать год выпуска
def prepare_grad_year(grad_year):
    return np.int64(re.search(r"\d{4}", grad_year).group())


# Получить пол по имени
def get_gender(name, n=1000):
    name_df = state.get("name_df")[:n]
    for row in name_df.to_dict(orient="records"):
        if name == row["text"]:
            return row["gender"] if row["gender"] in ["m", "f"] else None
    return None


# Получить и обработать возраст
def prepare_age(life_years, grad_year):
    return prepare_grad_year(grad_year) - np.int64(re.search(r"\d{4}", life_years).group())


# Получить и обработать тип карьеры
def prepare_type(cv_type):
    t = CVType()
    for k, v in {"нисходящ": t.negative, "стабильн": t.neutral, "восходящ": t.positive}.items():
        if k in cv_type:
            return v
    if "???" in cv_type:
        return t.neutral
    if "сохранение" in cv_type:
        return t.neutral
    if "понижение" in cv_type:
        return t.negative
    if "повышение" in cv_type:
        return t.positive
    return cv_type


# Определить, является ли ВУЗ столичным
def is_capital_university(university):
    text = Text(university)
    university = text.translate().lower()
    if "moscow" in university:
        return True
    if "petersburg" in university:
        return True
    capital_df = state.get("capital_df")
    for row in capital_df.to_dict(orient="records"):
        if row["city"] in university:
            return True
    return False


# Определить факультет естественных наук
def is_natural_faculty(faculty):
    if "???" in faculty:
        return False
    if "истор" in faculty:
        return False
    if "юрид" in faculty or "юрис" in faculty:
        return False
    return True


# Определить военно-медицинскую академию
def is_military_medical_university(university):
    text = Text(university)
    university = text.translate().lower()
    if "military-medical" in university:
        return True
    return False


# Получить данные о мужчинах и женщинах
def get_men_woman_df():
    df = state.get("df")
    men_df = pd.DataFrame(columns=df.columns.values)
    woman_df = pd.DataFrame(columns=df.columns.values)
    for row in df.to_dict(orient='records'):
        try:
            name = list(filter(lambda x: re.match(r'^\w{4,}$', x), row['name'].split(' ')))[:3]
            g = None
            for n in name:
                gender = get_gender(n)
                g = g if gender is None else gender
            if g is None:
                if name[0].endswith('а') or name[0].endswith('я'):
                    g = 'f'
                else:
                    g = 'm'
            if g == 'm':
                men_df.loc[-1] = row
                men_df.index = men_df.index + 1
            else:
                woman_df.loc[-1] = row
                woman_df.index = woman_df.index + 1
        except:
            pass
    return {"men_df": men_df, "woman_df": woman_df}


# Рассчитать статистику по мужчинам и женщинам
def stat_men_women():
    t = CVType()
    stat = {
        "total": {
            "men": 0,
            "women": 0
        },
        t.negative: {
            "men": 0,
            "women": 0,
        },
        t.neutral: {
            "men": 0,
            "women": 0
        },
        t.positive: {
            "men": 0,
            "women": 0
        },
        "other": {
            "men": 0,
            "women": 0
        }
    }
    men_woman_df = state.get("men_woman_df")
    men_df = men_woman_df["men_df"]
    woman_df = men_woman_df["woman_df"]
    stat["total"]["men"] = len(men_df)
    stat["total"]["women"] = len(woman_df)
    for cv_type in [t.negative, t.neutral, t.positive]:
        for mt in men_df["type"]:
            if prepare_type(mt) == cv_type:
                stat[cv_type]["men"] += 1
    for cv_type in [t.negative, t.neutral, t.positive]:
        for wt in woman_df["type"]:
            if prepare_type(wt) == cv_type:
                stat[cv_type]["women"] += 1
    for cv_type in [t.negative, t.neutral, t.positive]:
        stat["other"]["men"] += stat[cv_type]["men"]
        stat["other"]["women"] += stat[cv_type]["women"]
    stat["other"]["men"] = stat["total"]["men"] - stat["other"]["men"]
    stat["other"]["women"] = stat["total"]["women"] - stat["other"]["women"]
    return stat


# TODO: далее необходимо произвести остальные расчеты статистики
# Представлять результаты в виде отчетов с диаграммами в веб-интерфейсе
