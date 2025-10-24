from rest_framework.routers import DefaultRouter
from subscriptions.views import TariffView, UserSubscriptionView

router = DefaultRouter()
router.register(r'user-subscriptions', UserSubscriptionView, basename='user-subscriptions')
router.register(r'tariffs', TariffView, basename='tariffs')

urlpatterns = router.urls
