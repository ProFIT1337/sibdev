import csv
from io import TextIOWrapper

from django.db.models import QuerySet, Count, FilteredRelation, Q
from rest_framework import serializers

from .models import Operation, Customer, Gem
from .service import create_customers_and_gems_from_operations


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
        operations = Operation.objects.bulk_create(Operation(**operation) for operation in to_insert)
        create_customers_and_gems_from_operations(operations)
        return request


class FilterGemsSerializer(serializers.ListSerializer):

    def to_representation(self, data):
        new_data = data.filter(is_visable=True)
        return super().to_representation(new_data)


class GemListSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = FilterGemsSerializer
        model = Gem
        fields = ('name',)


class CustomerListSerializer(serializers.ModelSerializer):
    gems = GemListSerializer(read_only=True, many=True)

    class Meta:
        model = Customer
        fields = ('username', 'spent_money', 'gems')
