import requests
from terminaltables import AsciiTable


def get_all_pages_hh(vacancy):
    url = "https://api.hh.ru/vacancies"
    page = 0
    pages = 1
    data = []
    response = requests.get(url, params={'text': vacancy, 'area': 2})
    response.raise_for_status()
    while page < pages:
        page_response = requests.get(url, params={'text': vacancy, 'area': 2, 'page': page})
        page_response.raise_for_status()
        pages = page_response.json()['pages']
        page += 1
        items = page_response.json()['items']
        for i in range(len(items)):
            data.append(items[i])
    return data


def predict_rub_salary_hh(vacancy):
    data = get_all_pages_hh(vacancy)
    salary = []
    for i in range(len(data)):
        if data[i]['salary'] == None or data[i]['salary']['currency'] != "RUR":
          continue
        elif data[i]['salary']['to'] == None:
          salary.append(data[i]['salary']['from']*1.2)
        elif data[i]['salary']['from'] == None:
          salary.append(data[i]['salary']['to']*0.8)
        else:
          salary.append((data[i]['salary']['to'] + data[i]['salary']['from'])/2)
    return salary


def get_average_salary_hh(vacancy):
    url = "https://api.hh.ru/vacancies"
    average = {}
    response = requests.get(url, params={'text': vacancy, 'area': 2})
    response.raise_for_status()
    salary = predict_rub_salary_hh(vacancy)
    average_salary = int(sum(salary)/len(salary))
    average['vacancies_found'] = response.json()['found']
    average['vacancies_processed'] = len(salary)
    average['average_salary'] = average_salary
    return average


def get_all_pages_sj(vacancy):
    page = 0
    url = "https://api.superjob.ru/2.0/vacancies"
    headers = {"X-Api-App-Id": "v3.r.119100491.3d0fff6c37efbbc33054cc66e2afc94d10395b35.7922632be90283e6a4112316c51a98d15c16a052"}
    params = {"keyword": vacancy,
              "town": "14",
              "count": "100",
              "page": page}
    data = []
    response = requests.get(url, headers=headers, params = params)
    items = response.json()["objects"]
    for i in range(len(items)):
        data.append(items[i])
    while response.json()['more'] == True:
        page += 1
        response = requests.get(url, headers=headers, params={"keyword": vacancy, "town": "14", 'page': page, "count": "100"})
        items = response.json()['objects']
        for i in range(len(items)):
            data.append(items[i])
    return data


def predict_rub_salary_for_sj(vacancy):
    data = get_all_pages_sj(vacancy)
    salary = []
    for i in range(len(data)):
        if data[i]['payment'] == 0 or data[i]['payment'] == None:
            if data[i]['payment_from'] == 0 and data[i]['payment_to'] == 0:
                 continue
            elif data[i]['payment_from'] == 0:
                payment = int((data[i]['payment_to']*0.8))
            elif data[i]['payment_to'] == 0:
                payment = int((data[i]['payment_from']*1.2))
            else:
                payment = int((data[i]['payment_from'] + data[i]['payment_to']) / 2)
        else:
            payment = data[i]['payment']
        salary.append(payment)
    return salary


def get_average_salary_sj(vacancy):
    url = "https://api.superjob.ru/2.0/vacancies"
    headers = {"X-Api-App-Id": "v3.r.119100491.3d0fff6c37efbbc33054cc66e2afc94d10395b35.7922632be90283e6a4112316c51a98d15c16a052"}
    params = {"keyword": vacancy,
              "town": "14"}
    average = {}
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    salary = predict_rub_salary_for_sj(vacancy)
    average_salary = int(sum(salary)/len(salary))
    average['vacancies_found'] = response.json()['total']
    average['vacancies_processed'] = len(salary)
    average['average_salary'] = average_salary
    return average


def make_table_sj(vacancies):
    title = 'SuperJob'

    table_data = [
        ['Язык программирования', 'Ваканский найдено', 'Вакансий обработано', 'Средняя зарплата'],
        [list(vacancies.keys())[0], list(vacancies.values())[0]["vacancies_found"],
         list(vacancies.values())[0]['vacancies_processed'], list(vacancies.values())[0]['average_salary']],
        [list(vacancies.keys())[1], list(vacancies.values())[1]["vacancies_found"],
         list(vacancies.values())[1]['vacancies_processed'], list(vacancies.values())[1]['average_salary']],
        [list(vacancies.keys())[2], list(vacancies.values())[2]["vacancies_found"],
         list(vacancies.values())[2]['vacancies_processed'], list(vacancies.values())[2]['average_salary']],
    ]
    table = AsciiTable(table_data, title)
    print(table.table)


def make_table_hh(vacancies):
    title = 'HeadHunter'

    table_data = [
        ['Язык программирования', 'Ваканский найдено', 'Вакансий обработано', 'Средняя зарплата'],
        [list(vacancies.keys())[0], list(vacancies.values())[0]["vacancies_found"],
         list(vacancies.values())[0]['vacancies_processed'], list(vacancies.values())[0]['average_salary']],
        [list(vacancies.keys())[1], list(vacancies.values())[1]["vacancies_found"],
         list(vacancies.values())[1]['vacancies_processed'], list(vacancies.values())[1]['average_salary']],
        [list(vacancies.keys())[2], list(vacancies.values())[2]["vacancies_found"],
         list(vacancies.values())[2]['vacancies_processed'], list(vacancies.values())[2]['average_salary']],
    ]
    table = AsciiTable(table_data, title)
    print(table.table)


def main():
    vacancies = {}
    vacancies["Python"] = get_average_salary_sj("Программист Python")
    vacancies["Java"] = get_average_salary_sj("Программист Java")
    vacancies["C++"] = get_average_salary_sj("Программист C++")
    make_table_sj(vacancies)

    vacancies_hh = {}
    vacancies_hh["Python"] = get_average_salary_hh("Программист Python")
    vacancies_hh["Java"] = get_average_salary_hh("Программист Java")
    vacancies_hh["C++"] = get_average_salary_hh("Программист C++")
    make_table_hh(vacancies_hh)


main()

