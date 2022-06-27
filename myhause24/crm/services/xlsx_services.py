from datetime import datetime

from django.http import HttpResponse
from openpyxl import load_workbook
from io import BytesIO


def serializers_queryset(receipt, account, requisites, file):
    data = {
        'receiptNumber': receipt.number,
        'receiptDate': receipt.date.strftime("%d.%m.%Y"),
        'accountNumber': account.number,
        'receiptAddress': f'{receipt.apartment.owner} '
                          f'{receipt.apartment.house.address}, '
                          f'квартира {receipt.apartment.number}',
        'payCompany': requisites,
    }
    return write_to_file(file, data)


def write_to_file(file, data):
    template = load_workbook(filename=str(file.template.file))
    sheet = template.active
    for row in sheet.iter_rows():
        for cell in row:
            if cell.value in data.keys():
                sheet[cell.coordinate] = data[cell.value]
                print(cell.value)
    template.save(str(file.template.file))
    template.close()

# book = load_workbook('receipt_tpl.xlsx')
#
#
# sheet = book.active
# for row in sheet.iter_rows():
#     for cell in row:
#         if cell.value in json.keys():
#             sheet[cell.coordinate] = json[cell.value]
#             print(cell.value)
#
#
# book.save('receipt.xlsx')
# book.close()
