from rest_framework import generics

from .models import Operation, Customer
from .serializers import (
    CreateListOperationSerializer,
    CustomerListSerializer
)


class CreateListOperationView(generics.CreateAPIView):
    model = Operation
    serializer_class = CreateListOperationSerializer


class CustomerListView(generics.ListAPIView):
    serializer_class = CustomerListSerializer

    def get_queryset(self):
        customers = Customer.objects.order_by('-spent_money')[:5]
        return customers
