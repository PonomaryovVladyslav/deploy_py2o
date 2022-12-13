from django.utils import timezone
from rest_framework import serializers

from config.settings import RETURN_TIME_LIMIT
from store.models import Product, Purchase, MyUser, ReturnPurchase


class UserPurchaseSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(method_name='get_full_product_title')

    class Meta:
        model = Purchase
        fields = ['product', 'quantity', 'purchase_amount', 'date']

    def get_full_product_title(self, obj):
        return f'{obj.product.title} {obj.product.description}'


class MyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    purchases = UserPurchaseSerializer(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ['id', 'username', 'email', 'password', 'password2', 'deposit', 'purchases']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError('The two password fields dont match')
        return data

    def create(self, validated_data):
        user = MyUser(username=validated_data['username'],
                      email=validated_data['email'],
                      deposit=2000)
        user.set_password(validated_data['password'])
        user.save()
        return user


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'quantity']


class PurchaseCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = ['customer', 'product', 'quantity']
        read_only_fields = ['customer']

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')

        if quantity < 1:
            raise serializers.ValidationError({'quantity': 'Quantity must be greater than zero.'})

        if product.quantity < quantity:
            raise serializers.ValidationError({'quantity': 'Not enough goods in stock.'})

        customer_deposit = self.context.get('request').user.deposit

        if product.price * quantity > customer_deposit:
            raise serializers.ValidationError({'quantity': 'Not enough funds to make a purchase.'})

        return data


class PurchaseGetSerializer(serializers.ModelSerializer):
    customer = MyUserSerializer()
    product = serializers.SerializerMethodField(method_name='get_full_product_title')

    class Meta:
        model = Purchase
        fields = ['id', 'product', 'quantity', 'purchase_amount', 'date', 'customer']

    def get_full_product_title(self, obj):
        return f'{obj.product.title} {obj.product.description}'


class ReturnPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnPurchase
        fields = ['id', 'purchase', 'date']

    def validate_purchase(self, value):
        request = self.context.get('request')
        purchase_id = request.data.get('purchase')

        try:
            purchase = Purchase.objects.filter(customer=request.user).get(id=purchase_id)
        except Purchase.DoesNotExist:
            raise serializers.ValidationError('You dont have a purchase to return.')

        check_time_period = timezone.now() - purchase.date

        if check_time_period.seconds > RETURN_TIME_LIMIT:
            raise serializers.ValidationError('Return time has expired.')

        return value
