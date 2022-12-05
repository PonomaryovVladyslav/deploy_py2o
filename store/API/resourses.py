from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListAPIView, ListCreateAPIView

from store.API.serializers import ProductSerializer, PurchaseGetSerializer, PurchaseCreateSerializer, MyUserSerializer
from store.models import Product, Purchase, MyUser


class MyUserListCreateAPIView(ListCreateAPIView):
    queryset = MyUser.objects.all()
    serializer_class = MyUserSerializer


class ProductListCreateAPIView(ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class PurchaseListCreateAPIView(ListCreateAPIView):
    queryset = Purchase.objects.all()

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return PurchaseGetSerializer
        elif self.request.method.lower() == 'post':
            return PurchaseCreateSerializer

