# models.py

from typing import Any
from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField()
    unit_buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return self.name


class Purchase(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    purchase_date = models.DateField(auto_now_add=True)

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    sale_date = models.DateField(auto_now_add=True)
    profit = models.FloatField()


