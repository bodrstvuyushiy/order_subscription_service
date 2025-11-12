from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import SubscriptionPlan, UserSubscription

User = get_user_model()


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    tariff_type = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    price_with_discount = serializers.SerializerMethodField()

    class Meta:
        model = SubscriptionPlan
        fields = (
            "id",
            "subscribe_type",
            "price",
            "tariff_type",
            "discount_percent",
            "price_with_discount",
        )
        read_only_fields = fields

    def get_tariff_type(self, obj):
        return obj.get_tariff_type()

    def get_discount_percent(self, obj):
        return obj.get_discount_percent()

    def get_price_with_discount(self, obj):
        return obj.get_price_with_discount()


class UserSubscriptionSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    price_with_discount = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    tariff_type = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()

    class Meta:
        model = UserSubscription
        fields = (
            "id",
            "subscribe_type",
            "tariff_type",
            "discount_percent",
            "tariff",
            "user",
            "price",
            "price_with_discount",
        )
        read_only_fields = (
            "id",
            "tariff",
            "tariff_type",
            "discount_percent",
            "price",
            "price_with_discount",
        )

    def _get_plan(self, obj):
        if not hasattr(obj, "_plan_cache"):
            obj._plan_cache = (
                SubscriptionPlan.objects.filter(
                    subscribe_type__iexact=obj.subscribe_type, is_active=True
                )
                .select_related("tariff")
                .first()
            )
        return obj._plan_cache

    def get_tariff_type(self, obj):
        plan = self._get_plan(obj)
        if plan:
            return plan.get_tariff_type()
        if obj.tariff:
            return obj.tariff.tariff_type
        return None

    def get_discount_percent(self, obj):
        plan = self._get_plan(obj)
        if plan:
            return plan.get_discount_percent()
        if obj.tariff:
            return obj.tariff.discount_percent
        return 0

    def get_price_with_discount(self, obj):
        plan = self._get_plan(obj)
        if plan:
            return plan.get_price_with_discount()
        return Decimal(obj.price)

    def get_price(self, obj):
        return self.get_price_with_discount(obj)

    def validate_subscribe_type(self, value):
        try:
            plan = SubscriptionPlan.objects.get(
                subscribe_type__iexact=value, is_active=True
            )
        except SubscriptionPlan.DoesNotExist:
            raise serializers.ValidationError(f"План подписки '{value}' не найден.")
        return plan.subscribe_type

    def validate(self, attrs):
        if self.instance:
            allowed_fields = {"subscribe_type"}
            extra_fields = set(self.initial_data.keys()) - allowed_fields
            if extra_fields:
                raise serializers.ValidationError(
                    f"Нельзя менять поля: {', '.join(extra_fields)}"
                )
        return attrs

    def create(self, validated_data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError("Требуется аутентификация.")
        if UserSubscription.objects.filter(user=user).exists():
            raise serializers.ValidationError("У вас уже есть активная подписка.")
        return UserSubscription.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        subscribe_type = validated_data.get("subscribe_type")
        if subscribe_type:
            instance.subscribe_type = subscribe_type
        instance.save()
        return instance
