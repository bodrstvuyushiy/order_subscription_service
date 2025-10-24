from django.contrib.auth import get_user_model
from rest_framework import serializers
from products.models import Order
from service_app.config import PRODUCT_PRICES

User = get_user_model()


class OrderSerializer(serializers.ModelSerializer):
    total_price = serializers.DecimalField(max_digits=16, decimal_places=2, read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Order
        fields = ('user', 'product_name', 'price', 'quantity', 'total_price', 'created_at', 'updated_at', 'status')
        read_only_fields = ('price', 'total_price', 'created_at', 'updated_at', 'status')

    def get_total_price(self, obj):
        return obj.price * obj.quantity

    def validate(self, attrs):
        if self.instance:
            allowed_fields = {'product_name', "quantity"}
            extra_fields = set(self.initial_data.keys()) - allowed_fields
            if extra_fields:
                raise serializers.ValidationError(
                    f"Нельзя менять поля: {', '.join(extra_fields)}"
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Требуется аутентификация.")

        price = self._get_price_for_product(validated_data['product_name'])
        validated_data['price'] = price
        validated_data['status'] = 'pending'
        validated_data['user'] = user

        return Order.objects.create(**validated_data)

    def update(self, instance, validated_data):
        if 'product_name' in validated_data:
            instance.product_name = validated_data['product_name']
            instance.price = self._get_price_for_product(validated_data['product_name'])

        if 'quantity' in validated_data:
            instance.quantity = validated_data['quantity']

        instance.total_price = instance.price * instance.quantity

        instance.save()
        return instance

    def _get_price_for_product(self, product_name):
        return PRODUCT_PRICES.get(product_name, 0)
