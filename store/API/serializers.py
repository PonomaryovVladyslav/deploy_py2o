from rest_framework import serializers

from store.models import Product, Purchase, MyUser, ReturnPurchase


class UserPurchaseSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField(method_name='get_product_title')

    class Meta:
        model = Purchase
        fields = ('product', 'quantity', 'purchase_amount', 'date')

    def get_product_title(self, obj):
        return f'{obj.product.title} {obj.product.description}'


class MyUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    purchases = UserPurchaseSerializer(many=True, read_only=True)

    class Meta:
        model = MyUser
        fields = ('id', 'username', 'email', 'password', 'password2', 'deposit', 'purchases')

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
        fields = ('id', 'title', 'description', 'price', 'quantity')


class PurchaseCreateUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Purchase
        fields = ('customer', 'product', 'quantity')


class PurchaseGetSerializer(serializers.ModelSerializer):
    customer = MyUserSerializer()
    product = serializers.SerializerMethodField(method_name='get_product_title')

    class Meta:
        model = Purchase
        fields = ('id', 'product', 'quantity', 'purchase_amount', 'date', 'customer')

    def get_product_title(self, obj):
        return f'{obj.product.title} {obj.product.description}'


class ReturnPurchaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = ReturnPurchase
        fields = ('id', 'purchase', 'date')
