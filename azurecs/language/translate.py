"""
Michael duPont - michael@mdupont.com
"""

# pylint: disable=C0103

# stdlib
import json
# module
from azurecs import APITokenService
from azurecs.exceptions import exception_factory

class Translate(APITokenService):
    """Connection to the Azure Translate API"""

    base_url = 'http://api.microsofttranslator.com/V2/Ajax.svc'

    def translate(self, text: str, to: str, frm: str=None, **options) -> str:
        """Translate a given string into another language
        AzureCS detects the source language, but one can also be specified
        Additional keyword args are passed into the request parameters
        """
        params = {
            'category': 'general',
            'contentType': 'text/plain',
            'text': text.encode('utf8'),
            'to': to,
        }
        if frm is not None:
            params['from'] = frm
        if options is not None:
            params.update(options)
        return self.call('Translate', params)

    def translate_list(self, texts: [str], to: str, frm: str=None, **options) -> [dict]:
        """Translate a given list of strings into another language
        AzureCS detects the source language, but one can also be specified
        Additional keyword args are passed into the request parameters"""
        params = {
            'category': 'general',
            'contentType': 'text/plain',
            'texts': json.dumps(texts),
            'to': to,
        }
        if frm is not None:
            params['from'] = frm
        if options is not None:
            params.update(options)
        return self.call('TranslateArray', params)

    def detect(self, text: str) -> str:
        """Detects and returns the language code of a given string"""
        return self.call('Detect', {'text': text.encode('utf8')})

    def supported_langs(self) -> [str]:
        """Returns a list of language codes that AzureCS supports"""
        return self.call('GetLanguagesForTranslate')

    def handle_http_error(self, code: int, data: object):
        """Handle HTTP status code and AzureCS exceptions"""
        if isinstance(data, str) and 'Exception: ' in data:
            error = data.split(': ')
            raise exception_factory(error[0], ': '.join(error[1:]))
