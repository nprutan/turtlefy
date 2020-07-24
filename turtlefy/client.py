from requests import Session
from .hooks import handle_shopify_rate_limit


class TurtlefyClient(Session):
    '''
    A Requests Session object with stored
    Shopify credentials in the request headers.
    Also a few conveniences for managing API paths.
    '''

    def __init__(self, base_uri, token=None, api_version=None):
        super().__init__()
        self._base_uri = base_uri
        self.api_version = api_version
        self.token = token
        self.hooks['response'].append(handle_shopify_rate_limit)

    @property
    def base_uri(self):
        return (f'https://{self._base_uri}.myshopify.com'
                if not '://' in self._base_uri else self._base_uri)

    @property
    def api_path(self):
        return f'{self.base_uri}/admin/api/{self.api_version}'

    @property
    def gql_endpoint(self):
        return f'{self.base_uri}/admin/api/{self.api_version}/graphql.json'

    def update_token(self, token):
        self.headers['X-Shopify-Access-Token'] = token

    def update_gql_headers(self):
        self.headers['Content-Type'] = 'application/graphql'


def get_turtlefy_client(base_uri, token, api_version='2020-07', type=None):
    turtle_client = TurtlefyClient(base_uri, token, api_version=api_version)

    if not turtle_client.token:
        raise ValueError('Please provide token')
    turtle_client.headers.update({
        'X-Shopify-Access-Token': f'{turtle_client.token}',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    return turtle_client
