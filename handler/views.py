from rest_framework import generics

from .models import Operation, Customer
from .serializers import (
    CreateListOperationSerializer,
    CustomerListSerializer
)
from .service import create_customers_from_operations


class CreateListOperationView(generics.CreateAPIView):
    model = Operation
    serializer_class = CreateListOperationSerializer


class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerListSerializer

    def get_queryset(self):
        create_customers_from_operations()
        customers = Customer.objects.order_by('-spent_money')[:5]
        return customers
