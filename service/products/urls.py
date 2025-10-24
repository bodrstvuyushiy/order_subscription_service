from rest_framework.routers import DefaultRouter
from products.views import OrderView

router = DefaultRouter()
router.register(r'orders', OrderView, basename='orders')

urlpatterns = router.urls
