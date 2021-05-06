from django.urls import path

from .views import CreateListOperationView

urlpatterns = [
    path('', CreateListOperationView.as_view()),
]
