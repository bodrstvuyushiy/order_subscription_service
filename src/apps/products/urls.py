from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderView, ProductItemViewSet

orders_router = DefaultRouter()
orders_router.register(r"", OrderView, basename="orders")

products_router = DefaultRouter()
products_router.register(r"", ProductItemViewSet, basename="product-items")

urlpatterns = [
    path("orders/", include(orders_router.urls)),
    path("products/", include(products_router.urls)),
]
