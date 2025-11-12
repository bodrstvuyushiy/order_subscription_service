from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscriptionPlanView, UserSubscriptionView

user_router = DefaultRouter()
user_router.register(
    r"user-subscriptions", UserSubscriptionView, basename="user-subscriptions"
)

plan_list = SubscriptionPlanView.as_view({"get": "list"})
plan_detail = SubscriptionPlanView.as_view({"get": "retrieve"})

urlpatterns = [
    path("", plan_list, name="subscription-plan-list"),
    path("<int:pk>/", plan_detail, name="subscription-plan-detail"),
    path("", include(user_router.urls)),
]
