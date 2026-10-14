import requests


REQUEST_SUCCESS_CODE = 100
VERIFY_SUCCESS_CODES = (100, 101)
ALREADY_VERIFIED_CODE = 101


class ZarinpalError(Exception):
    def __init__(self, message, *, code=None, status_code=None, response=None):
        super().__init__(message)
        self.code = code
        self.status_code = status_code
        self.response = response


class ZarinpalPaymentRequest:
    def __init__(self, authority, code, message, fee, fee_type, payment_url):
        self.authority = authority
        self.code = code
        self.message = message
        self.fee = fee
        self.fee_type = fee_type
        self.payment_url = payment_url


class ZarinpalVerification:
    def __init__(self, code, message, ref_id, card_pan, card_hash, fee, fee_type):
        self.code = code
        self.message = message
        self.ref_id = ref_id
        self.card_pan = card_pan
        self.card_hash = card_hash
        self.fee = fee
        self.fee_type = fee_type

    @property
    def verified(self):
        return self.code in VERIFY_SUCCESS_CODES

    @property
    def already_verified(self):
        return self.code == ALREADY_VERIFIED_CODE


class ZarinpalClient:
    def __init__(self, merchant_id, api_base_url, start_pay_url, currency="IRR", timeout=15):
        if not merchant_id:
            raise ZarinpalError("Zarinpal merchant id is not configured.")
        if not api_base_url or not start_pay_url:
            raise ZarinpalError("Zarinpal URLs are not configured.")
        if currency not in ("IRR", "IRT"):
            raise ZarinpalError("Zarinpal currency must be IRR or IRT.")

        self.merchant_id = merchant_id
        self.currency = currency
        self.timeout = timeout
        self.api_base_url = api_base_url.rstrip("/")
        self.start_pay_url = start_pay_url if start_pay_url.endswith("/") else f"{start_pay_url}/"
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "Content-Type": "application/json",
        })

    def payment_url(self, authority):
        return f"{self.start_pay_url}{authority}"

    def request_payment(self, amount, description, callback_url, mobile=None, email=None, order_id=None):
        payload = {
            "merchant_id": self.merchant_id,
            "amount": self._amount(amount),
            "currency": self.currency,
            "description": description,
            "callback_url": callback_url,
        }
        metadata = {}
        if mobile:
            metadata["mobile"] = mobile
        if email:
            metadata["email"] = email
        if order_id:
            metadata["order_id"] = str(order_id)
        if metadata:
            payload["metadata"] = metadata

        data = self._post("/request.json", payload)
        if data.get("code") != REQUEST_SUCCESS_CODE or not data.get("authority"):
            raise ZarinpalError(
                data.get("message") or "Zarinpal did not create a payment.",
                code=data.get("code"),
                response=data,
            )

        authority = data["authority"]
        return ZarinpalPaymentRequest(
            authority=authority,
            code=data.get("code"),
            message=data.get("message") or "",
            fee=data.get("fee"),
            fee_type=data.get("fee_type") or "",
            payment_url=self.payment_url(authority),
        )

    def verify_payment(self, amount, authority):
        data = self._post("/verify.json", {
            "merchant_id": self.merchant_id,
            "amount": self._amount(amount),
            "authority": authority,
        })
        if data.get("code") not in VERIFY_SUCCESS_CODES:
            raise ZarinpalError(
                data.get("message") or "Zarinpal did not verify the payment.",
                code=data.get("code"),
                response=data,
            )

        return ZarinpalVerification(
            code=data.get("code"),
            message=data.get("message") or "",
            ref_id=data.get("ref_id"),
            card_pan=data.get("card_pan") or "",
            card_hash=data.get("card_hash") or "",
            fee=data.get("fee"),
            fee_type=data.get("fee_type") or "",
        )

    def _amount(self, amount):
        try:
            value = int(amount)
        except (TypeError, ValueError) as exc:
            raise ZarinpalError("Zarinpal amount is invalid.") from exc
        if value <= 0:
            raise ZarinpalError("Zarinpal amount is invalid.")
        return value

    def _post(self, endpoint, payload):
        try:
            response = self.session.post(
                f"{self.api_base_url}{endpoint}",
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise ZarinpalError("Could not connect to Zarinpal.") from exc

        try:
            body = response.json()
        except ValueError as exc:
            raise ZarinpalError(
                "Invalid response from Zarinpal.",
                status_code=response.status_code,
            ) from exc

        if not isinstance(body, dict):
            raise ZarinpalError("Invalid response from Zarinpal.", status_code=response.status_code, response=body)

        data = body.get("data")
        errors = body.get("errors")
        if not isinstance(data, dict) or errors:
            code = errors.get("code") if isinstance(errors, dict) else None
            raise ZarinpalError(
                self._error_message(errors, response.status_code),
                code=code,
                status_code=response.status_code,
                response=body,
            )

        return data

    @staticmethod
    def _error_message(errors, status_code):
        if isinstance(errors, dict) and errors.get("message"):
            return str(errors["message"])
        if isinstance(errors, list) and errors:
            first = errors[0]
            if isinstance(first, dict) and first.get("message"):
                return str(first["message"])
            if first:
                return str(first)
        return f"Zarinpal request failed ({status_code})."


def get_zarinpal_client():
    from core.site_config import get_site_settings

    site = get_site_settings()
    if site is None:
        raise ZarinpalError("Zarinpal is not configured.")

    return ZarinpalClient(
        merchant_id=(site.zarinpal_merchant_id or "").strip(),
        api_base_url=(site.zarinpal_api_base_url or "").strip(),
        start_pay_url=(site.zarinpal_start_pay_url or "").strip(),
        currency=(site.zarinpal_currency or "").strip(),
    )
