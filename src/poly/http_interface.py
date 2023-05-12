import requests

from .poly_result import build_result


class HttpInterface:
    _base_url = ''

    def request(self, query, language, namespace, use_cache):
        if self._base_url == '':
            print('URL to Polypheny is not set!')
            return None
        print('Requesting to:', self._base_url, '\t Query:', query)
        req = {'query': query,
               'analyze': False,
               'cache': use_cache,
               'language': language,
               'database': namespace}
        url = f'{self._base_url}/{language}'
        return build_result(requests.post(url, json=req).json()[-1])  # return only the last result

    def set_url(self, url):
        url = url.strip(" /'\"")
        if not url:
            raise ValueError('Submitted URL is invalid')
        print('setting url to:', url)
        self._base_url = url

    def __str__(self):
        if not self._base_url:
            return "NO URL is set"
        return f"Database: {self._base_url}"
