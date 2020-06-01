from requests import Session


class TurtlefyClient(Session):
    def __init__(self, base_uri, token=None, api_version=None):
        super().__init__()
        self._base_uri = base_uri
        self.api_version = api_version
        self.token = token

    @property
    def base_uri(self):
        return (f'https://{self._base_uri}.myshopify.com'
        if not '://' in self._base_uri else self._base_uri)

    @property
    def api_path(self):
        return f'{self.base_uri}/admin/api/{self.api_version}'


def get_turtlefy_client(base_uri, token, api_version='2020-04'):
    turtle_client = TurtlefyClient(base_uri, token, api_version=api_version)

    if not turtle_client.token:
        raise ValueError('Please provide token')
    turtle_client.headers.update(
        {'X-Shopify-Access-Token': f'{turtle_client.token}'})
    return turtle_client
