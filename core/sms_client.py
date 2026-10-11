import requests

from core.enums import MedianaPanel


EDGE_BASE_URL = 'https://edge.ippanel.com'
NEW_BASE_URL = 'https://api.mediana.ir'
PANEL_BASE_URLS = {
    MedianaPanel.EDGE: EDGE_BASE_URL,
    MedianaPanel.NEW: NEW_BASE_URL,
}


class MedianaAPIError(Exception):
    def __init__(self, message, *, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class MedianaClient:
    def __init__(self, base_url: str, api_key: str, from_number: str, panel: str = MedianaPanel.EDGE, timeout: int = 15):
        if not base_url or not api_key or not from_number:
            raise MedianaAPIError("Mediana is not configured for this website.")

        self.timeout = timeout
        self.base_url = base_url.rstrip("/")
        self.from_number = from_number
        self.panel = panel if panel in MedianaPanel.values else MedianaPanel.EDGE
        self.session = requests.Session()

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if self.panel == MedianaPanel.NEW:
            headers["X-API-KEY"] = api_key
        else:
            headers["Authorization"] = api_key
        self.session.headers.update(headers)

    @staticmethod
    def request_id(data):
        if not isinstance(data, dict):
            return None
        if data.get('bulk_id'):
            return str(data['bulk_id'])
        inner = data.get('data')
        if isinstance(inner, dict):
            value = inner.get('requestCode') or inner.get('requestId')
            if value not in (None, ''):
                return str(value)
        return None

    def _error_message(self, data, status_code):
        if isinstance(data, dict):
            meta = data.get('meta')
            if isinstance(meta, dict) and meta.get('errorMessage'):
                return str(meta['errorMessage'])
            inner = data.get('data')
            if isinstance(inner, dict) and inner.get('message'):
                return str(inner['message'])
        return f"Mediana request failed ({status_code})."

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
            if self.panel != MedianaPanel.NEW:
                raise MedianaAPIError(
                    {
                        "status_code": response.status_code,
                        "response": data,
                    }
                )
            raise MedianaAPIError(
                self._error_message(data, response.status_code),
                status_code=response.status_code,
                response=data,
            )

        if self.panel == MedianaPanel.NEW and isinstance(data, dict):
            meta = data.get('meta')
            if isinstance(meta, dict) and meta.get('errorMessage'):
                raise MedianaAPIError(
                    str(meta['errorMessage']),
                    status_code=response.status_code,
                    response=data,
                )
            inner = data.get('data')
            if isinstance(inner, dict) and inner.get('succeed') is False:
                raise MedianaAPIError(
                    str(inner.get('message') or 'Mediana rejected the message.'),
                    status_code=response.status_code,
                    response=data,
                )

        return data

    def _with_request_id(self, responses):
        last = responses[-1]
        ids = [self.request_id(item) for item in responses]
        ids = [item for item in ids if item]
        if isinstance(last, dict) and ids:
            last = dict(last)
            last['bulk_id'] = ','.join(ids)
        return last

    def send_pattern(
        self,
        *,
        recipients: list[str],
        pattern_code: str,
        parameters: dict,
    ):
        if self.panel == MedianaPanel.NEW:
            responses = [
                self._post(
                    "/sms/v1/send/pattern",
                    {
                        "sendingNumber": self.from_number,
                        "recipients": [recipient],
                        "patternCode": pattern_code,
                        "parameters": parameters,
                    },
                )
                for recipient in recipients
            ]
            return self._with_request_id(responses)

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
