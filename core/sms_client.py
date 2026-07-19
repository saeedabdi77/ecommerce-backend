import requests

from django.conf import settings


class MedianaAPIError(Exception):
    pass


class MedianaClient:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.base_url = settings.MEDIANA_BASE_URL.rstrip("/")
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": settings.MEDIANA_API_KEY,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

    def _post(self, endpoint: str, payload: dict):
        try:
            response = self.session.post(
                f"{self.base_url}{endpoint}",
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise MedianaAPIError("Could not connect to Mediana.") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise MedianaAPIError("Invalid response from Mediana.") from exc

        if not response.ok:
            raise MedianaAPIError(
                {
                    "status_code": response.status_code,
                    "response": data,
                }
            )

        return data

    def send_pattern(
        self,
        *,
        recipients: list[str],
        pattern_code: str,
        parameters: dict,
    ):
        print(recipients, pattern_code, parameters)
        return self._post(
            "/v1/api/send",
            {
                "sending_type": "pattern",
                "recipients": recipients,
                "code": pattern_code,
                "params": parameters,
                "from_number": settings.MEDIANA_FROM_NUMBER,
            },
        )
