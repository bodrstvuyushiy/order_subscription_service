from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.subscriptions.models import SubscriptionPlan, Tariff

pytestmark = pytest.mark.django_db


def test_catalog_contains_discount_and_final_price():
    discount_tariff = Tariff.objects.create(tariff_type="discount", discount_percent=20)
    SubscriptionPlan.objects.create(
        subscribe_type="Mountain", price=Decimal("2500.00"), tariff=discount_tariff
    )
    client = APIClient()

    response = client.get("/api/subscriptions/")  # act

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    plan = data[0]
    assert plan["discount_percent"] == 20
    assert plan["tariff_type"] == "discount"
    assert float(plan["price_with_discount"]) == pytest.approx(2000.0)
