from rest_framework.permissions import BasePermission
from subscriptions.models import UserSubscription


class HasActiveSubscription(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return UserSubscription.objects.filter(
            user=request.user,
            is_active=True
        ).exists()
