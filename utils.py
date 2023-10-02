import openpyxl
import logging
import os
import db


def process_sheet(source, storage, city):
    row = 3
    try:
        while source[f'A{row}'].value is not None:
            name = source[f'B{row}'].value
            fullname = ''
            note = ''
            if '(' in name:
                fullname, note = name[:-1].split(' (')
            else:
                fullname = name

            position = source[f'C{row}'].value
            team = source[f'D{row}'].value
            head = ''
            match city:
                case 'moscow':
                    head = 'МСК'
                case 'novgorod':
                    head = 'НН'
                case 'podolsk':
                    head = 'Подольск'
                case 'saratov':
                    head = 'Саратов'
                case 'spb':
                    head = 'СПб'
                case 'stavropol':
                    head = 'Ставрополь'
                case 'tumen':
                    head = 'Тюмень'
                case 'administration':
                    head = 'АГПП'

            temp = {
                'position': position.strip(),
                'team': team.strip(),
                'head': head.strip(),
                'note': note.strip(),
            }

            if fullname in storage.keys():
                storage[fullname].append(temp)
            else:
                storage[fullname] = [temp]

            # db.insert_user(name, position, team, head)

            row += 1

    except ValueError as e:
        logging.error(f'While processing the Excel sheet an error occurred\nInfo: {e}')

    logging.info('Data was successfully loaded from Excel sheet')


def save_data(storage):
    try:
        for filename in os.scandir('data'):
            if filename.is_file():
                book = openpyxl.load_workbook(filename.path)
                sheet = book.active
                process_sheet(sheet, storage, filename.name[:-5])

    except FileNotFoundError:
        logging.error('File table.xlsx not found')


def user_access(name, storage):
    return name in storage.keys()


if __name__ == '__main__':
    data = {}
    save_data(data)
