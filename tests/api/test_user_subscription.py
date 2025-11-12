from decimal import Decimal

import pytest
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from apps.subscriptions.models import SubscriptionPlan, Tariff, UserSubscription
from apps.users.models import CustomUser

pytestmark = pytest.mark.django_db


@pytest.fixture
def authenticated_client():
    client = APIClient()
    user = CustomUser.objects.create_user(
        username="subscriber", email="sub@example.com", password="pass123"
    )
    token = Token.objects.create(user=user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
    return client, user


@pytest.fixture
def subscription_plan():
    Tariff.objects.create(tariff_type="full", discount_percent=0)
    discount_tariff = Tariff.objects.create(tariff_type="discount", discount_percent=15)
    return SubscriptionPlan.objects.create(
        subscribe_type="Sky", price=Decimal("5000.00"), tariff=discount_tariff
    )


def test_create_subscription_returns_discounted_price(
    authenticated_client, subscription_plan
):
    client, user = authenticated_client
    request_payload = {"subscribe_type": subscription_plan.subscribe_type}

    response = client.post(
        "/api/subscriptions/user-subscriptions/",
        request_payload,
        format="json",
    )  # act

    assert response.status_code == 201
    data = response.json()
    assert data["subscribe_type"] == subscription_plan.subscribe_type
    assert data["tariff_type"] == "discount"
    assert data["discount_percent"] == 15
    assert float(data["price_with_discount"]) == pytest.approx(4250.0)
    assert UserSubscription.objects.filter(
        user=user, subscribe_type=subscription_plan.subscribe_type
    ).exists()


def test_second_subscription_is_rejected(authenticated_client, subscription_plan):
    client, user = authenticated_client
    UserSubscription.objects.create(
        user=user,
        subscribe_type=subscription_plan.subscribe_type,
        tariff=subscription_plan.tariff,
    )
    request_payload = {"subscribe_type": subscription_plan.subscribe_type}

    response = client.post(
        "/api/subscriptions/user-subscriptions/",
        request_payload,
        format="json",
    )  # act

    assert response.status_code == 400
