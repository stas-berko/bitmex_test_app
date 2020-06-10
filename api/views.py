import django
from django.shortcuts import render

# Create your views here.
from rest_framework import mixins, generics, status
from rest_framework.response import Response

from .bitmex_config import Bitmex
from .models import Order, Account
from .serializers import OrderSerializer, AccountSerializer


class AccountCreate(generics.CreateAPIView):
    serializer_class = AccountSerializer
    queryset = Account.objects.all()


class OrderList(mixins.ListModelMixin,
                generics.CreateAPIView):
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        try:
            account = self.request.query_params['account']
            user = Account.objects.get(name=account)
        except (django.core.exceptions.MultipleObjectsReturned, django.core.exceptions.ObjectDoesNotExist, KeyError):
            return Response({}, status=status.HTTP_401_UNAUTHORIZED)
        bitmex_user = Bitmex(user)
        order = bitmex_user.create_order(**request.data)
        if order:
            order.update({"account": user})
            new_order = Order(**order)
            new_order.save()

            serializer = OrderSerializer(new_order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        username = self.request.query_params.get('account', None)
        if username is not None:
            queryset = Order.objects.filter(account__name=username)
            return queryset


class OrderDetail(mixins.RetrieveModelMixin,
                  mixins.DestroyModelMixin,
                  generics.GenericAPIView):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_queryset(self):
        username = self.request.query_params.get('account', None)
        if username is not None:
            queryset = Order.objects.filter(account__name=username)
            return queryset
