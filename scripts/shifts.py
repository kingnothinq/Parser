from datetime import datetime

import pdfplumber


def update():
    pass

def duty():
    pdf = pdfplumber.open("test.pdf")
    tables = pdf.pages[0].extract_tables()
    tables.pop()
    current_date = datetime.now()
    current_year = str(current_date.year)
    current_month = current_date.month
    current_day = str(current_date.day)
    months = {1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель', 5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
              9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'}

    for table in tables:
        date = table[0][0].replace('\n', '').split(' ')
        month = date[0].replace(' ', '')
        year = date[1].replace(' ', '').replace('г.', '')
        if year == current_year and month == months[current_month]:
            for row in table[2:]:
                if str(row[table[0].index(current_day)]) == '4':
                    person = row[1]

    return datetime.date(current_date), person
