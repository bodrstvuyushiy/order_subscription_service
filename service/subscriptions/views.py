from django.db.models import ExpressionWrapper, F, DecimalField
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from subscriptions.models import UserSubscription, Tariff
from subscriptions.serializers import TariffSerializer, UserSubscriptionSerializer
from service_app.config import SUBSCRIPTION_PRICES
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated


class TariffView(ReadOnlyModelViewSet):
    queryset = Tariff.objects.only('tariff_type', 'discount_percent')
    serializer_class = TariffSerializer


class UserSubscriptionView(ModelViewSet):
    queryset = (
        UserSubscription.objects
        .select_related("tariff", "user")
        .annotate(
            price_with_discount=ExpressionWrapper(
                F("price") * (100 - F("tariff__discount_percent")) / 100.0,
                output_field=DecimalField(max_digits=10, decimal_places=2)
            )
        )
        .only("id", "subscribe_type", "price", "tariff__tariff_type", "tariff__discount_percent", "user__id",  "user")
    )

    def get_permissions(self):
        # Разрешаем list без аутентификации, остальное — только авторизованным
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]


    def list(self, request, *args, **kwargs):
        data = [
            {"subscribe_type": key, "price": SUBSCRIPTION_PRICES.get(key, 0)}
            for key in ("human", "mountain", "sky")
        ]
        return Response(data)

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return qs.filter(user=self.request.user)
        return qs

    serializer_class = UserSubscriptionSerializer
    lookup_field = "pk"



