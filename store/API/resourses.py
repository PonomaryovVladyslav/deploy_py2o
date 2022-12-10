from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter

from store.API.filters import CustomerPurchaseFilter, PurchaseProductPriceFilter, CustomerProductFilter, \
    CustomerReturnsFilter
from store.API.permissions import IsAdminOrReadOnly, IsAuthenticatedReadAndCreate
from store.API.serializers import ProductSerializer, PurchaseGetSerializer, MyUserSerializer, \
    ReturnPurchaseSerializer, PurchaseCreateUpdateSerializer
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

    def perform_create(self, serializer):
        title = serializer.validated_data['title'] + " !"
        serializer.save(title=title)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    filter_backends = [CustomerPurchaseFilter,
                       PurchaseProductPriceFilter]
    permission_classes = [IsAuthenticatedReadAndCreate]

    def get_serializer_class(self):
        if self.request.method.lower() == 'get':
            return PurchaseGetSerializer
        return PurchaseCreateUpdateSerializer

    def perform_create(self, serializer):
        serializer.save(customer=self.request.user)


class ReturnPurchaseViewSet(viewsets.ModelViewSet):
    queryset = ReturnPurchase.objects.all()
    serializer_class = ReturnPurchaseSerializer
    filter_backends = [CustomerReturnsFilter]
    permission_classes = [IsAuthenticatedReadAndCreate]
