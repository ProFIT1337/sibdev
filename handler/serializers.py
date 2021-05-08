import csv
from io import TextIOWrapper

from rest_framework import serializers

from .models import Operation, Customer, Gem
from .service import create_customers_and_gems_from_operations, clear_db


class CreateListOperationSerializer(serializers.ModelSerializer):
    """Сериализатор операций(Operation). Обрабатывает загруженную таблицу"""
    file = serializers.FileField()

    class Meta:
        model = Operation
        fields = ('file',)

    def create(self, request):
        """
            Парсит полученную таблицу и сохраняет полученные данные в БД
            Данные об операциях в модель Operations
            Данные о камнях в модель Gem
            Данные о покупателях в модель Customer
        """
        clear_db()
        csv_file = TextIOWrapper(request.get('file'), encoding='utf8')
        reader = csv.reader(csv_file)
        next(reader, None)
        operations_to_insert = []
        for row in reader:
            operation = {
                'customer': row[0],
                'item': row[1],
                'total': int(row[2]),
                'quantity': int(row[3]),
                'date': row[4]
            }
            operations_to_insert.append(operation)
        operations = Operation.objects.bulk_create(Operation(**operation) for operation in operations_to_insert)
        create_customers_and_gems_from_operations(operations)
        return request


class FilterGemsSerializer(serializers.ListSerializer):
    """Фильтрует список камней по атрибуту is_visible"""

    def to_representation(self, data):
        new_data = data.filter(is_visible=True)
        return super().to_representation(new_data)


class GemListSerializer(serializers.ModelSerializer):
    """Сериализатор камней(Gem)"""

    class Meta:
        list_serializer_class = FilterGemsSerializer
        model = Gem
        fields = ('name',)


class CustomerListSerializer(serializers.ModelSerializer):
    """Сериализатор покупателей(Customer)"""
    gems = GemListSerializer(read_only=True, many=True)

    class Meta:
        model = Customer
        fields = ('username', 'spent_money', 'gems')
