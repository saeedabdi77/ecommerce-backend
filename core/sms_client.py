import requests


class MedianaAPIError(Exception):
    pass


class MedianaClient:
    def __init__(self, base_url: str, api_key: str, from_number: str, timeout: int = 15):
        if not base_url or not api_key or not from_number:
            raise MedianaAPIError("Mediana is not configured for this website.")

        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.from_number = from_number
        self.session = requests.Session()

        self.session.headers.update(
            {
                "Authorization": api_key,
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
        return self._post(
            "/v1/api/send",
            {
                "sending_type": "pattern",
                "recipients": recipients,
                "code": pattern_code,
                "params": parameters,
                "from_number": self.from_number,
            },
        )
