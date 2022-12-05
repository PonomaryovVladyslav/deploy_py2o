from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from store.API.serializers import ProductSerializer, PurchaseGetSerializer, MyUserSerializer, \
    ReturnPurchaseSerializer, PurchaseCreateUpdateSerializer
from store.models import Product, Purchase, MyUser, ReturnPurchase


class UserViewSet(viewsets.ModelViewSet):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data['title'] + " !"
        serializer.save(title=title)


class PurchaseViewSet(viewsets.ModelViewSet):

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return PurchaseGetSerializer
        return PurchaseCreateUpdateSerializer

    def get_queryset(self):
        queryset = Purchase.objects.all()
        if self.request.method.lower() == 'get':
            price = self.request.query_params.get('price', 'No params')
            if price.isdigit():
                return queryset.filter(product__price__gte=price)
        return queryset


class ReturnPurchaseViewSet(viewsets.ModelViewSet):
    queryset = ReturnPurchase.objects.all()
    serializer_class = ReturnPurchaseSerializer

