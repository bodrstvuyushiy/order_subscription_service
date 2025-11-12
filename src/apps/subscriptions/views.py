from django.db.models import F
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from .models import SubscriptionPlan, UserSubscription
from .serializers import SubscriptionPlanSerializer, UserSubscriptionSerializer


class SubscriptionPlanView(ReadOnlyModelViewSet):
    queryset = (
        SubscriptionPlan.objects.filter(is_active=True)
        .select_related("tariff")
        .order_by("subscribe_type")
    )
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [AllowAny]


class UserSubscriptionView(ModelViewSet):
    queryset = UserSubscription.objects.select_related("tariff", "user").annotate(
        price_with_discount=F("price")
    )
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action in ("retrieve", "update", "partial_update", "destroy"):
            return qs.filter(user=self.request.user)
        return qs

    serializer_class = UserSubscriptionSerializer
    lookup_field = "pk"
