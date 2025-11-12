from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from apps.products.models import ProductItem

pytestmark = pytest.mark.django_db


def test_catalog_is_public_and_filters_inactive():
    ProductItem.objects.create(
        name="Активный товар", price=Decimal("100.00"), is_active=True
    )
    ProductItem.objects.create(
        name="Неактивный товар", price=Decimal("200.00"), is_active=False
    )
    client = APIClient()

    response = client.get("/api/products/")  # act

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["name"] == "Активный товар"
