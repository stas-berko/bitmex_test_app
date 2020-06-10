from django.db import models


class Account(models.Model):
    name = models.CharField(max_length=24, null=False)
    api_key = models.CharField(max_length=24, null=False)
    api_secret = models.CharField(max_length=48, null=False)


class Order(models.Model):
    BUY = 'B'
    SELL = 'S'
    SIDE_VARIANT = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]

    order_id = models.CharField(max_length=36, null=False, primary_key=True, blank=False)
    symbol = models.CharField(max_length=10, null=False)
    volume = models.IntegerField(null=False)
    timestamp = models.DateTimeField(null=False)
    side = models.CharField(max_length=1, choices=SIDE_VARIANT, default=BUY, null=False)
    price = models.DecimalField(max_digits=24, decimal_places=12, null=False)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
