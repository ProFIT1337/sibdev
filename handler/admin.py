from django.contrib import admin

from .models import Operation, Customer, Gem

admin.site.register(Operation)
admin.site.register(Customer)
admin.site.register(Gem)
