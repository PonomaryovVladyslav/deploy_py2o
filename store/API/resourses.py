from django.db import transaction
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from store.API.filters import CustomerPurchaseFilter, PurchaseProductPriceFilter, CustomerProductFilter, \
    CustomerReturnsFilter
from store.API.permissions import IsAdminOrReadOnly, IsAuthenticatedReadAndCreate
from store.API.serializers import ProductSerializer, PurchaseGetSerializer, MyUserSerializer, \
    ReturnPurchaseSerializer, PurchaseCreateSerializer
from store.models import Product, Purchase, MyUser, ReturnPurchase


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = MyUserSerializer
    queryset = MyUser.objects.all()
    filter_backends = [CustomerProductFilter]
    permission_classes = [permissions.IsAdminUser]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [OrderingFilter]
    ordering_fields = ['title', 'price', 'quantity']
    permission_classes = [IsAdminOrReadOnly]


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    filter_backends = [CustomerPurchaseFilter,
                       PurchaseProductPriceFilter]
    permission_classes = [IsAuthenticatedReadAndCreate]

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return PurchaseGetSerializer
        return PurchaseCreateSerializer

    def perform_create(self, serializer):
        customer = self.request.user
        product = serializer.validated_data.get('product')
        quantity = serializer.validated_data.get('quantity')

        product.quantity -= quantity
        customer.deposit -= product.price * quantity

        with transaction.atomic():
            product.save()
            customer.save()
            serializer.save(customer=customer)


class ReturnPurchaseViewSet(viewsets.ModelViewSet):
    queryset = ReturnPurchase.objects.all()
    serializer_class = ReturnPurchaseSerializer
    filter_backends = [CustomerReturnsFilter]
    permission_classes = [IsAuthenticatedReadAndCreate]

    @action(detail=True, methods=['post'])
    def approve_return(self, request, pk=None):
        purchase = get_object_or_404(Purchase, returnpurchase=pk)
        customer = purchase.customer
        product = purchase.product

        customer.deposit += purchase.purchase_amount
        product.quantity += purchase.quantity

        with transaction.atomic():
            purchase.delete()
            customer.save()
            product.save()

        return Response({'status': 'return approved'})
