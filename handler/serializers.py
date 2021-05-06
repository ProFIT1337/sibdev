from rest_framework import serializers

from .models import Operation, Customer


class ParseTableSerializer(serializers.Serializer):
    """Сериализатор обработывающий загруженную таблицу"""



    def create(self, validated_data):
        """Парсит таблицу и сохраняет полученные данные в БД"""



