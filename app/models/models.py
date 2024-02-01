import datetime

from fastapi import FastAPI
from pydantic import BaseModel
from googletrans import Translator
import time

app = FastAPI()


# Хранение общих данных - состояния
class State(dict):
    def get(self, key):
        if key not in self:
            raise ValueError("non-existent key specified")
        return self[key]

    def set(self, key, value):
        self[key] = value


# Хранение Н/С/В типов карьеры и операции над ними
class CVType(BaseModel):
    negative: str = "negative"
    neutral: str = "neutral"
    positive: str = "positive"

    # Получить краткое наименование - заглавную первую букву
    @staticmethod
    def short(text):
        return text.upper()[0]

    # Получить краткие наименования
    def get_short(self):
        return {cv_type: self.short(cv_type) for cv_type in [self.negative, self.neutral, self.positive]}


# Пара для хранения временного отрезка лет и операций над ним
# from_year - начало отрезка
# to_year - конец отрезка
class YearPair(BaseModel):
    from_year: int = 0
    to_year: int = 0

    # Получить длину отрезка в годах
    def get_length(self):
        return self.to_year - self.from_year

    # Получить длину отрезка [from_year, year] в годах, где
    # year - указанный год, from_year <= year <= now
    # now - текущий год
    # Нужно для вычисления возраста респондента на <year> год
    def get_length_from_year(self, year):
        now = datetime.date.today().year
        if self.from_year > year or now < year:
            raise ValueError("invalid year specified")
        return year - self.from_year


# Хранение текста и операции над ним
class Text(BaseModel):
    value: str = ""

    def __init__(self, value, **data):
        super().__init__(**data)
        self.value = value

    # Перевод
    def translate(self, lang='en', api_delay=0.3):
        # задержка запроса API для снижения нагрузки на переводчик
        # см. https://cloud.google.com/translate/quotas
        time.sleep(api_delay)
        translator = Translator()
        translated = translator.translate(self.value, dest=lang)
        return translated.text

    def clean(self):
        pass


# Анкета
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
class Form(BaseModel):
    no: int
    name: str
    life_years: YearPair
    grad_year: int
    faculty: str
    university: str
    rus_cv: Text
    fc_cv: Text
    type: CVType
    place: str


state: State = State()
