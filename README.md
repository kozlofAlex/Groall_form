# [Groall](https://groall.noda.pro/test_qa)
Тестирование формы "Вывод средств со счета"

[Тестовая документация](https://docs.google.com/spreadsheets/d/1XSLXysYEPzcn2ZQx7stjbxF3ymXPbQeKhEBTCcwr4BM/edit?usp=sharing)



1. #### `pip install -r requirements.txt`

2. #### `playwright install`

3. Запустить тесты через Терминал, выполнив команду:

   - #### `pytest tests/API_UI_test.py --browser chromium --headed`               - прогон всех тестов
   - #### `pytest tests/API_UI_test.py -m "api"`                                  - API тесты
   - #### `pytest tests/API_UI_test.py -m "ui" --headed`                          - UI тесты

## Отчет: 
![allure_отчет](https://github.com/kozlofAlex/Groall_form/assets/107295846/fcf5aba1-b51c-4bef-baaf-dce7f86c74e1)
