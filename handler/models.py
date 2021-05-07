from django.db import models


class Operation(models.Model):
    """Торговая операция"""
    customer = models.CharField('Логин покупателя', max_length=50)
    item = models.CharField('Купленный камень', max_length=50)
    total = models.PositiveIntegerField('Сумма')
    quantity = models.PositiveSmallIntegerField('Количество купленных камней')
    date = models.DateTimeField('Дата и время операции')

    def __str__(self):
        return f'Операция покупателя: {self.customer}'


class Customer(models.Model):
    """Покупатель"""
    username = models.CharField('Логин', max_length=100)
    spent_money = models.PositiveIntegerField('Сумма потраченных средств', default=0)
    gems = models.JSONField('Купленные камни')


    def __str__(self):
        return self.username
