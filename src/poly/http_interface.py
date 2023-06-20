import requests

from .poly_result import build_result


class HttpInterface:
    _base_url = ''

    def request(self, query, language, namespace):
        if self._base_url == '':
            print('URL to Polypheny is not yet set! Use %poly db: <url> to set the url')
            return None
        req = {'query': query,
               'analyze': False,
               'cache': True,
               'language': language,
               'database': namespace}
        url = f'{self._base_url}/{language}'
        return build_result(requests.post(url, json=req).json()[-1])  # return only the last result

    def set_url(self, url):
        url = url.strip(" /'\"")
        if not url:
            raise ValueError('Submitted URL is invalid')
        self._base_url = url

    def __str__(self):
        if not self._base_url:
            return "NO URL is set"
        return f"Database: {self._base_url}"
