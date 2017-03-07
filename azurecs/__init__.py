"""
Michael duPont - michael@mdupont.com
"""

# pylint: disable=C0321

# stdlib
from datetime import datetime, timedelta
# libraries
import requests

class APIService:
    """Service class to handle web API services"""

    base_url = None

    def __init__(self, api_key: str):
        self.api_key = api_key

    def call(self, endpoint: str, body: str=None, params: {str: object}=None,
             headers: {str: object}=None, return_error: bool=False) -> {str: object}:
        """Make a call to service's given endpoint and request information
        Returns the response string or dictionary if successful
        Will raise an HTTPError is status code is not 200
        If return_error is True, the error response will be returned with no exception raised
        """
        url = self.base_url + '/' + endpoint
        headers = headers if headers is not None else {}
        headers.update({'Ocp-Apim-Subscription-Key': self.api_key})

        resp = requests.get(url, data=body, params=params, headers=headers)
        resp.encoding = 'UTF-8-sig'
        data = resp.json()

        if resp.status_code != 200 and not return_error:
            self.handle_http_error(resp.status_code, data)

        return data

    def handle_http_error(self, code: int, data: object):
        """Handle HTTP status code and AzureCS exceptions"""
        raise NotImplementedError('No HTTP error handling has been defined')

class AzureAuthToken:
    """Class to make sure that .value is always a valid 10-min auth token"""
    _token = None
    last_fetched = None

    def __init__(self, api_key: str):
        self.azure_api_key = api_key

    @property
    def value(self) -> str:
        """The value of the current auth token"""
        if self._token is None or self.outdated:
            self.update()
        return self._token

    @property
    def outdated(self) -> bool:
        """Returns True if a new token value must be fetched"""
        return self.last_fetched is None or \
               datetime.utcnow() > self.last_fetched+timedelta(minutes=9)

    def update(self):
        """Fetch a new auth token value"""
        url = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
        headers = {'Ocp-Apim-Subscription-Key': self.azure_api_key}
        resp = requests.post(url, headers=headers)
        self._token = resp.text
        self.last_fetched = datetime.utcnow()

class APITokenService:
    """Service class to handle tokenized services still on Data Market"""

    base_url = None

    def __init__(self, api_key: str):
        self.authtoken = AzureAuthToken(api_key)

    def call(self, endpoint: str, params: {str: object}=None,
             return_error: bool=False) -> 'str or dict':
        """Make a call to service's given endpoint with the given parameters
        Returns the response string or dictionary if successful
        Resends the call if the auth token is not accepted
        Else raises an arbitrary error determined by Azure Cognitive Services
        NOTE: Exceptions are triggered when response is a string containing 'Exception: '
        """
        url = self.base_url + '/' + endpoint
        headers = {'Authorization': 'Bearer {}'.format(self.authtoken.value)}

        resp = requests.get(url, params=params, headers=headers)
        resp.encoding = 'UTF-8-sig'
        data = resp.json()

        if resp.status_code != 200 and not return_error:
            if isinstance(data, str) and 'Exception: ' in data:
                if data.startswith("ArgumentException: The incoming token has expired"):
                    self.authtoken.update()
                    return self.call(endpoint, params)
            else:
                self.handle_http_error(resp.status_code, data)

        return data

    def handle_http_error(self, code: int, data: object):
        """Handle HTTP status code and AzureCS exceptions"""
        raise NotImplementedError('No HTTP error handling has been defined')
