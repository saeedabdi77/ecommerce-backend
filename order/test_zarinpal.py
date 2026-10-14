import unittest
from unittest.mock import Mock, patch

from order.zarinpal import ZarinpalClient, ZarinpalError


API_BASE_URL = "https://sandbox.zarinpal.com/pg/v4/payment"
START_PAY_URL = "https://sandbox.zarinpal.com/pg/StartPay/"


class ZarinpalClientTests(unittest.TestCase):
    def setUp(self):
        self.client = ZarinpalClient(
            merchant_id="merchant-id",
            api_base_url=API_BASE_URL,
            start_pay_url=START_PAY_URL,
            currency="IRT",
        )

    def test_request_payment_uses_sandbox_and_returns_start_pay_url(self):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {
            "data": {
                "code": 100,
                "message": "Success",
                "authority": "A0001",
                "fee_type": "Merchant",
                "fee": 0,
            },
            "errors": [],
        }

        with patch.object(self.client.session, "post", return_value=response) as post:
            result = self.client.request_payment(
                amount=150000,
                description="Order 1001",
                callback_url="https://shop.example/callback",
                mobile="09120000000",
                order_id=1001,
            )

        self.assertEqual(result.authority, "A0001")
        self.assertEqual(result.payment_url, "https://sandbox.zarinpal.com/pg/StartPay/A0001")
        self.assertEqual(post.call_args.args[0], f"{API_BASE_URL}/request.json")
        payload = post.call_args.kwargs["json"]
        self.assertEqual(payload["amount"], 150000)
        self.assertEqual(payload["currency"], "IRT")
        self.assertEqual(payload["metadata"]["order_id"], "1001")

    def test_verify_payment_treats_101_as_already_verified(self):
        response = Mock(ok=True, status_code=200)
        response.json.return_value = {
            "data": {
                "code": 101,
                "message": "Verified",
                "ref_id": 55,
                "card_pan": "502229******5995",
                "card_hash": "hash",
                "fee_type": "Merchant",
                "fee": 0,
            },
            "errors": [],
        }

        with patch.object(self.client.session, "post", return_value=response):
            result = self.client.verify_payment(150000, "A0001")

        self.assertTrue(result.verified)
        self.assertTrue(result.already_verified)
        self.assertEqual(result.ref_id, 55)

    def test_gateway_error_raises(self):
        response = Mock(ok=False, status_code=422)
        response.json.return_value = {
            "data": [],
            "errors": {"code": -9, "message": "Validation error"},
        }

        with patch.object(self.client.session, "post", return_value=response):
            with self.assertRaises(ZarinpalError) as raised:
                self.client.request_payment(1000, "Order", "https://shop.example/callback")

        self.assertEqual(raised.exception.code, -9)
        self.assertEqual(str(raised.exception), "Validation error")

    def test_client_uses_configured_urls(self):
        client = ZarinpalClient(
            merchant_id="merchant-id",
            api_base_url="https://payment.zarinpal.com/pg/v4/payment",
            start_pay_url="https://payment.zarinpal.com/pg/StartPay",
        )
        self.assertEqual(client.api_base_url, "https://payment.zarinpal.com/pg/v4/payment")
        self.assertEqual(client.payment_url("A0001"), "https://payment.zarinpal.com/pg/StartPay/A0001")

    def test_missing_merchant_id_raises(self):
        with self.assertRaises(ZarinpalError):
            ZarinpalClient(merchant_id="", api_base_url=API_BASE_URL, start_pay_url=START_PAY_URL)
