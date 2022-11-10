from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    deposit = models.DecimalField(max_digits=7, decimal_places=2, blank=True, null=True)


class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=250)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    quantity = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ['title']
        verbose_name = 'product'
        verbose_name_plural = 'products'

    def __str__(self):
        return self.title


class Purchase(models.Model):
    customer = models.ForeignKey(MyUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveSmallIntegerField()
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']
        verbose_name = 'purchase'
        verbose_name_plural = 'purchases'

    def __str__(self):
        return f'{self.product}'


class ReturnPurchase(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date']

    def __str__(self):
        return f'{self.purchase}'
