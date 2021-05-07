from django.urls import path

from .views import CreateListOperationView, CustomerListView

urlpatterns = [
    path('', CreateListOperationView.as_view()),
    path('result', CustomerListView.as_view()),

]
