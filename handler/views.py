from rest_framework import generics

from .models import Operation, Customer
from .serializers import (
    CreateListOperationSerializer
)


class CreateListOperationView(generics.CreateAPIView):
    model = Operation
    serializer_class = CreateListOperationSerializer
