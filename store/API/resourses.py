from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from store.API.serializers import ProductSerializer, PurchaseGetSerializer, MyUserSerializer, \
    ReturnPurchaseSerializer, PurchaseCreateUpdateSerializer, UserProductSerializer
from store.models import Product, Purchase, MyUser, ReturnPurchase


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = MyUserSerializer

    def get_queryset(self):
        queryset = MyUser.objects.all()
        if self.request.method.lower() == 'get':
            product_title = self.request.query_params.get('product_title')
            if product_title:
                return queryset.filter(purchases__product__title__icontains=product_title)
        return queryset

    @action(detail=True, methods=['get'])
    def get_customer_product(self, request, pk=None):
        customer = self.get_object()
        serializer = UserProductSerializer(customer)
        return Response(serializer.data)


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
            product_price = self.request.query_params.get('product_price', 'No params')
            if product_price.isdigit():
                return queryset.filter(product__price__gte=product_price)
        return queryset


class ReturnPurchaseViewSet(viewsets.ModelViewSet):
    queryset = ReturnPurchase.objects.all()
    serializer_class = ReturnPurchaseSerializer

