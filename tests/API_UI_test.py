"""
Варианты запуска:
1. pytest tests/API_UI_test.py --browser chromium --headed               - прогон всех тестов
2. pytest tests/API_UI_test.py -m "api"                                  - только API тесты
3. pytest tests/API_UI_test.py -m "ui" --browser chromium --headed       - UI тесты в chromium
   pytest tests/API_UI_test.py -m "ui" --browser webkit --headed         - UI тесты в webkit
   pytest tests/API_UI_test.py -m "ui" --browser firefox --headed        - UI тесты в firefox
Формирование отчета:
pytest --alluredir=results tests/API_UI_test.py --headed
allure serve results
"""

import re
import pytest
import conftest
import requests
from playwright.sync_api import Playwright, sync_playwright, expect


@pytest.mark.api
# FORMS-01:	Вывод средств со счета
def test_correct_value():
    """
    Тест не проходит из-за бага (система не конвертирует токены в коины):
    В наличии 122000 токенов (1220 коинов), в поле вводим коины = 1220
    Значит в ответе должно вернуться введенное значение * 100, то есть сообщение:
    "Токены списаны, всего списано 122000, осталось 0", но приходит:
    "Токены списаны, всего списано 1220, осталось 120780"
    """
    payload = {
        'actionForm': 'sendToken',
        'secret': '2d$JHjqml=',
        'value': 1220
    }
    r = requests.post(conftest.baseUrl, headers=conftest.headers, data=payload)
    s = [int(s) for s in re.findall(r'-?\d+\.?\d*', r.text)]
    # print(r.text)
    assert r.status_code == 200
    assert payload.get('value') * 100 == s[0]
    assert s[1] == 0


@pytest.mark.api
# FORMS-02:	Вывод средств, больше, чем есть на счете
def test_biggest_value():
    """
    Баг: система позволяет списать количество средств > чем на балансе
    То есть второе число в ответе  - отрицательное
    """
    payload = {
        'actionForm': 'sendToken',
        'secret': '2d$JHjqml=',
        'value': 122001
    }
    r = requests.post(conftest.baseUrl, headers=conftest.headers, data=payload)
    s = [int(s) for s in re.findall(r'-?\d+\.?\d*', r.text)]
    assert r.status_code == 200
    assert s[1] >= 0


@pytest.mark.api
# FORMS-03:	Вывод дробного значения
def test_fractional_value():
    """
    Имеется блокирующий баг: FORMS-01
    """
    payload = {
        'actionForm': 'sendToken',
        'secret': '2d$JHjqml=',
        'value': 1219.99
    }
    r = requests.post(conftest.baseUrl, headers=conftest.headers, data=payload)
    s = [float(s) for s in re.findall(r'-?\d+\.?\d*', r.text)]
    assert r.status_code == 200
    assert payload.get('value') * 100 == s[0]


@pytest.mark.ui
# FORMS-04: Ввод пустого значения в поле вывода коинов
def test_empty_value(page):
    """
    Проверка валидационного сообщения, в случае когда не было введено значение
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле обязательно для заполнения"


@pytest.mark.ui
# FORMS-05: Ввод некорректного значения (спецсимвола)
def test_valid_spec(page):
    """
    Проверка валидационного сообщения, в случае когда введено не число
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("input[name=\"value\"]").fill("12+12")
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле должно содержать только цифры!"


@pytest.mark.ui
# FORMS-06: Ввод строкового значения
def test_valid_text(page):
    """
    Проверка валидационного сообщения, в случае когда введено не число
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("input[name=\"value\"]").fill("qwerty")
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле должно содержать только цифры!"


@pytest.mark.ui
# FORMS-07: Ввод эмоджи
def test_valid_emoji(page):
    """
    Проверка валидационного сообщения, в случае когда введено эмоджи
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("input[name=\"value\"]").fill('👽')
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле должно содержать только цифры!"


@pytest.mark.api
# FORMS-08: Вывод значения "0"
def test_value_zero():
    """
    Проверка сообщения когда было введено значение 0
    """
    payload = {
        'actionForm': 'sendToken',
        'secret': '2d$JHjqml=',
        'value': 0
    }
    r = requests.post(conftest.baseUrl, headers=conftest.headers, data=payload)
    s = [int(s) for s in re.findall(r'-?\d+\.?\d*', r.text)]
    assert r.status_code == 200
    assert r.text == 'Введеное кол-во коинов должно быть больше 0'


@pytest.mark.api
# FORMS-09: Вывод отрицательного значения
def test_negative_value():
    """
    Проверка сообщения когда было введено отрицательное значение
    """
    payload = {
        'actionForm': 'sendToken',
        'secret': '2d$JHjqml=',
        'value': -10
    }
    r = requests.post(conftest.baseUrl, headers=conftest.headers, data=payload)
    s = [int(s) for s in re.findall(r'-?\d+\.?\d*', r.text)]
    assert r.status_code == 200
    assert r.text == 'Введеное кол-во коинов должно быть больше 0'


@pytest.mark.ui
# FORMS-10:	Установка чекбокса "Вывести всё" до ввода значения
def test_valid_check(page):
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("#all").check()
    page.get_by_role("button", name="Вывести").click()
    expect(page.locator("#all")).to_be_checked()


@pytest.mark.ui
# FORMS-12: Ввод SQL-инъекции
def test_sql(page):
    """
    Проверка валидационного сообщения когда введено эмоджи
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("input[name=\"value\"]").fill('SELECT * FROM users')
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле должно содержать только цифры!"


@pytest.mark.ui
# FORMS-13: Устойчивость к XSS-атакам
def test_XSS(page):
    """
    Проверка валидационного сообщения когда введено эмоджи
    """
    page.goto("https://groall.noda.pro/test_qa")
    page.get_by_title("Close").click()
    page.locator("input[name=\"value\"]").fill('<script>alert(«I hacked this!»)</script>')
    page.get_by_role("button", name="Вывести").click()
    assert page.locator("#value-error").text_content() == "Поле должно содержать только цифры!"

