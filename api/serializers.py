from rest_framework import serializers
from .models import Order, Account


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'symbol', 'volume', 'timestamp', 'side', 'price', 'account']


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['name', 'api_key', 'api_secret']
