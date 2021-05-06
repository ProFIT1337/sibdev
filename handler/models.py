from django.db import models


class Gem(models.Model):
    name = models.CharField('Название камня', max_length=50)

    def __str__(self):
        return self.name


class Customer(models.Model):
    """Покупатель"""
    username = models.CharField('Логин', max_length=100)
    spent_money = models.PositiveIntegerField('Сумма потраченных средств', default=0)
    gems = models.ManyToManyField(Gem, verbose_name='Купленные камни')

    def __str__(self):
        return self.username
