import logging

from django.db.models import DecimalField, ExpressionWrapper, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from apps.subscriptions.permissions import HasActiveSubscription
from .models import Order, ProductItem
from .serializers import OrderSerializer, ProductItemSerializer
from .tasks import send_order_notification

logger = logging.getLogger(__name__)


@method_decorator(cache_page(60 * 5), name="list")
@method_decorator(cache_page(60 * 5), name="retrieve")
class ProductItemViewSet(ReadOnlyModelViewSet):
    queryset = ProductItem.objects.filter(is_active=True).order_by("name")
    serializer_class = ProductItemSerializer
    permission_classes = [AllowAny]


class OrderView(ModelViewSet):
    queryset = Order.objects.annotate(
        total_price=ExpressionWrapper(
            F("price") * F("quantity"),
            output_field=DecimalField(max_digits=10, decimal_places=2),
        )
    )
    serializer_class = OrderSerializer
    lookup_field = "pk"
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.is_staff:
            return qs
        return qs.filter(user=user)

    def perform_create(self, serializer):
        instance = serializer.save()
        send_order_notification.delay(instance.id)
