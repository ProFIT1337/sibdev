from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import generics, status
from rest_framework.parsers import FileUploadParser, MultiPartParser, FormParser
from rest_framework.response import Response

from .models import Operation, Customer
from .serializers import (
    CreateListOperationSerializer,
    CustomerListSerializer
)


class CreateListOperationView(generics.CreateAPIView):
    """Контроллер для загрузки таблицы операций(Operation)"""
    model = Operation
    serializer_class = CreateListOperationSerializer
    parser_classes = (MultiPartParser, FormParser, FileUploadParser)

    def post(self, request, *args, **kwargs):
        try:
            super().post(request, *args, **kwargs)
        except ValidationError as e:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={
                    'Status': 'Error',
                    'Desc': f'{e.message}- в процессе обработки файла произошла ошибка.'
                }
            )
        return Response(status=status.HTTP_201_CREATED, data={'Status': 'Файл был обработан без ошибок'})


class CustomerListView(generics.ListAPIView):
    """Контроллер вывода результатов работы"""
    serializer_class = CustomerListSerializer

    @method_decorator(cache_page(60 * 60 * 2))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        """Получаем только 5 покупателей, потративших наибольшую сумму"""
        customers = Customer.objects.order_by('-spent_money')[:5]
        return customers
