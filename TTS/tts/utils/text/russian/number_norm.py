import re
from typing import Dict
from num2words import num2words

_comma_number_re = re.compile(r"([0-9][0-9\,]+[0-9])")
_decimal_number_re = re.compile(r"([0-9]+\,[0-9]+)")
_currency_re = re.compile(r"(₽|\$|€|¥)([0-9\,\.]*[0-9]+)")
_ordinal_re = re.compile(r"[0-9]+(-?(й|го|я|е|ая|ое|ий|ее|ые|их|ие))")
_number_re = re.compile(r"-?[0-9]+")


def _remove_commas(m):
    return m.group(1).replace(",", "")


def _expand_decimal_point(m):
    return m.group(1).replace(",", " запятая ")


def __expand_currency(value: str, inflection: Dict[float, str]) -> str:
    parts = value.replace(",", "").split(".")
    if len(parts) > 2:
        return f"{value} {inflection[2]}"  # Unexpected format
    text = []
    integer = int(parts[0]) if parts[0] else 0
    if integer > 0:
        integer_unit = inflection.get(integer, inflection[2])
        text.append(f"{integer} {integer_unit}")
    fraction = int(parts[1]) if len(parts) > 1 and parts[1] else 0
    if fraction > 0:
        fraction_unit = inflection.get(fraction / 100, inflection[0.02])
        text.append(f"{fraction} {fraction_unit}")
    if len(text) == 0:
        return f"ноль {inflection[2]}"
    return " ".join(text)


def _expand_currency(m: "re.Match") -> str:
    currencies = {
        "$": {
            0.01: "цент",
            0.02: "цента",
            1: "доллар",
            2: "доллара",
        },
        "€": {
            0.01: "евроцент",
            0.02: "евроцента",
            1: "евро",
            2: "евро",
        },
        "£": {
            0.01: "пенни",
            0.02: "пенса",
            1: "фунт стерлингов",
            2: "фунта стерлингов",
        },
        "¥": {
            0.01: "сень",
            0.02: "сена",
            1: "йена",
            2: "йены",
        },
        "₽": {
            0.01: "копейка",
            0.02: "копейки",
            1: "рубль",
            2: "рубля",
        },
    }
    unit = m.group(1)
    currency = currencies[unit]
    value = m.group(2)
    return __expand_currency(value, currency)


def _expand_ordinal(m):
    num = int(m.group(0))
    ordinal_word = num2words(num, lang='ru', to='ordinal')
    return ordinal_word


def _expand_number(m):
    num = int(m.group(0))
    return num2words(num, lang='ru')


def normalize_numbers(text):
    text = re.sub(_comma_number_re, _remove_commas, text)
    text = re.sub(_currency_re, _expand_currency, text)
    text = re.sub(_decimal_number_re, _expand_decimal_point, text)
    text = re.sub(_ordinal_re, _expand_ordinal, text)
    text = re.sub(_number_re, _expand_number, text)
    return text
