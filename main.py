import requests
from terminaltables import AsciiTable
from dotenv import load_dotenv
import os


def get_all_pages_hh(vacancy):
    url = "https://api.hh.ru/vacancies"
    page = 0
    pages = 1
    vacancies = []
    response = requests.get(url, params={'text': vacancy, 'area': 2})
    response.raise_for_status()
    while page < pages:
        page_response = requests.get(url, params={'text': vacancy, 'area': 2, 'page': page})
        page_response.raise_for_status()
        data_vacancy = page_response.json()
        pages = data_vacancy['pages']
        page += 1
        items = data_vacancy['items']
        count_items = len(items)
        for i in range(count_items):
            vacancies.append(items[i])
    return vacancies


def predict_rub_salary_hh(vacancy):
    vacancies = get_all_pages_hh(vacancy)
    average_salary_a = []
    for vacancy in vacancies:
        if vacancy['salary'] is None:
            continue
        else:
            salary_from = vacancy["salary"]["from"]
            salary_to = vacancy["salary"]["to"]
            average_salary_a.append(predict_salary(salary_from, salary_to))
    return average_salary_a


def get_average_salary_hh(vacancy):
    url = "https://api.hh.ru/vacancies"
    average = []
    response = requests.get(url, params={'text': vacancy, 'area': 2})
    response.raise_for_status()
    salary = predict_rub_salary_hh(vacancy)
    average_salary = int(sum(salary)/len(salary))
    average.append(response.json()['found'])
    average.append(len(salary))
    average.append(average_salary)
    return average


def get_all_pages_sj(vacancy):
    load_dotenv()
    token = os.getenv("TOKEN_SJ")
    page = 0
    url = "https://api.superjob.ru/2.0/vacancies"
    headers = {"X-Api-App-Id": token}
    params = {"keyword": vacancy,
              "town": "14",
              "count": "100",
              "page": page}
    data = []
    response = requests.get(url, headers=headers, params=params)
    data_vacancies = response.json()
    items = data_vacancies["objects"]
    count_items = len(items)
    for i in range(count_items):
        data.append(items[i])
    while data_vacancies['more'] is True:
        page += 1
        response = requests.get(url, headers=headers, params={"keyword": vacancy, "town": "14", 'page': page, "count": "100"})
        items = response.json()['objects']
        count_items = len(items)
        for i in range(count_items):
            data.append(items[i])
    return data


def predict_salary(salary_from, salary_to):
    if salary_to is None:
        salary = salary_from * 1.2
    elif salary_from is None:
        salary = salary_to * 0.8
    else:
        salary = (salary_to + salary_from) / 2
    return salary


def predict_rub_salary_for_sj(vacancy):
    vacancies = get_all_pages_sj(vacancy)
    average_salary_a = []
    for vacancy in vacancies:
        salary_from = vacancy['payment_from']
        salary_to = vacancy['payment_to']
        if vacancy['payment'] == 0 or vacancy['payment'] is None:
            average_salary_a.append(predict_salary(salary_from, salary_to))
        else:
            payment = vacancy['payment']
            average_salary_a.append(payment)
    return average_salary_a


def get_average_salary_sj(vacancy):
    url = "https://api.superjob.ru/2.0/vacancies"
    headers = {"X-Api-App-Id": "v3.r.119100491.3d0fff6c37efbbc33054cc66e2afc94d10395b35.7922632be90283e6a4112316c51a98d15c16a052"}
    params = {"keyword": vacancy,
              "town": "14"}
    average = []
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    salary = predict_rub_salary_for_sj(vacancy)
    average_salary = int(sum(salary)/len(salary))
    average.append(response.json()['total'])
    average.append(len(salary))
    average.append(average_salary)
    return average


def make_table(title_table):
    languages = [
        'Java',
        'C++',
        'Python',
        'Php',
        'C',
        'C#',
    ]

    table_data = [['Язык программирования', 'Ваканский найдено', 'Вакансий обработано', 'Средняя зарплата']]
    for language in languages:
        table_row = [language]
        if title_table.find("unter") == -1:
            info = get_average_salary_sj("Программист "+language)
        elif title_table.find("unter") > 0:
            info = get_average_salary_hh("Программист "+language)
        table_row.append(info[0])
        table_row.append(info[1])
        table_row.append(info[2])
        table_data.append(table_row)
    return AsciiTable(table_data, title_table).table


def main():
    print(make_table("Superjob"))
    print(make_table("HeadHunter"))


main()


