"""
Michael duPont - michael@mdupont.com
"""

# module
from azurecs import APIService
from azurecs.exceptions import exception_factory, httpcode_exception

class SpellCheck(APIService):
    """Connection to the Bing Spell Check API"""

    base_url = 'https://api.cognitive.microsoft.com/bing/v5.0/spellcheck'

    def check(self, text: str, **options) -> {str: object}:
        """Spell check a given string and return any flagged tokens
        Additional keyword args are passed into the request parameters
        """
        params = {
            'contentType': 'text/plain',
            'text': text.encode('utf8')
        }
        if options is not None:
            params.update(options)
        resp = self.call('', params=params)
        if 'flaggedTokens' in resp:
            return resp['flaggedTokens']
        return resp

    def handle_http_error(self, code: int, data: object):
        """Handle HTTP status code and AzureCS exceptions"""
        if isinstance(data, dict):
            if 'statusCode' in data:
                raise httpcode_exception(code, data['message'])
            elif 'errors' in data:
                error = data['errors'][0]
                error_code, error_msg = error['code'], error['message']
                raise exception_factory(error_code, error_msg)
