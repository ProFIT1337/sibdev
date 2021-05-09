import csv
from io import TextIOWrapper

from django.core.cache import cache
from django.core.validators import FileExtensionValidator
from rest_framework import serializers

from .models import Operation, Customer, Gem
from .service import clear_db, create_customer, push_data_to_db, create_operation, parse_file


class CreateListOperationSerializer(serializers.ModelSerializer):
    """Сериализатор операций(Operation). Обрабатывает загруженную таблицу"""
    file = serializers.FileField(validators=[FileExtensionValidator(['csv'])])

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
        cache.clear()

        file = request.get('file')
        csv_file = TextIOWrapper(file, encoding='utf8')
        reader = csv.reader(csv_file)
        next(reader, None)
        customers_to_insert, gems_set, operations_to_insert = parse_file(reader)

        push_data_to_db(customers_to_insert, gems_set, operations_to_insert)
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
