from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.products.models import Order, ProductItem
from apps.subscriptions.models import SubscriptionPlan, Tariff, UserSubscription
from apps.users.models import CustomUser

pytestmark = pytest.mark.django_db


@pytest.fixture
def subscribed_client():
    client = APIClient()
    user = CustomUser.objects.create_user(
        username="buyer",
        email="buyer@example.com",
        password="pass123",
        telegram_id="321",
    )
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

    base_tariff = Tariff.objects.create(tariff_type="full", discount_percent=0)
    plan = SubscriptionPlan.objects.create(
        subscribe_type="Human", price=Decimal("1000.00"), tariff=base_tariff
    )
    UserSubscription.objects.create(
        user=user, subscribe_type=plan.subscribe_type, tariff=base_tariff
    )

    return client


@pytest.fixture
def product_factory():
    def _create(**overrides):
        defaults = {
            "name": "Голограмма",
            "price": Decimal("5000.00"),
            "is_active": True,
        }
        defaults.update(overrides)
        return ProductItem.objects.create(**defaults)

    return _create


@patch("apps.products.views.send_order_notification.delay")
def test_create_order(mock_task, subscribed_client, product_factory):
    product = product_factory()
    request_payload = {"product_name": product.name, "quantity": 2}

    response = subscribed_client.post(
        "/api/orders/",
        request_payload,
        format="json",
    )  # act

    assert response.status_code == 201
    payload = response.json()
    assert float(payload["total_price"]) == pytest.approx(10000.0)
    mock_task.assert_called_once()
    assert Order.objects.filter(id=payload["id"]).exists()


def test_zero_quantity_is_rejected(subscribed_client, product_factory):
    product = product_factory()
    request_payload = {"product_name": product.name, "quantity": 0}

    response = subscribed_client.post(
        "/api/orders/",
        request_payload,
        format="json",
    )  # act

    assert response.status_code == 400
    assert "quantity" in response.json()
