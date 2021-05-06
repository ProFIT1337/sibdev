import csv
from io import TextIOWrapper

from rest_framework import serializers

from .models import Operation, Customer


class CreateListOperationSerializer(serializers.ModelSerializer):
    """Сериализатор обработывающий загруженную таблицу"""
    file = serializers.FileField()

    class Meta:
        model = Operation
        fields = ('file',)

    def create(self, request):
        """Парсит таблицу и сохраняет полученные данные в БД"""
        Operation.objects.all().delete()
        csv_file = TextIOWrapper(request.get('file'), encoding='utf8')
        reader = csv.reader(csv_file)
        next(reader, None)
        to_insert = []
        for row in reader:
            operation = {
                'customer': row[0],
                'item': row[1],
                'total': int(row[2]),
                'quantity': int(row[3]),
                'date': row[4]
            }
            to_insert.append(operation)
        Operation.objects.bulk_create(Operation(**operation) for operation in to_insert)
        return request
