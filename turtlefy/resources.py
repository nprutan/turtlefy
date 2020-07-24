
def get_webhooks(client):
    return client.get(f'{client.api_path}/webhooks.json').json()['webhooks']


def update_webhooks_url(client, hooks, new_url):
    results = []
    for hook in hooks:
        url = f'{client.api_path}/webhooks/{hook["id"]}.json'
        payload = {
                "webhook": {
                    "id": hook['id'],
                    "address": new_url
                    }
                }
        results.append(client.put(url, json=payload).json())
    return results


def get_order_risks(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/risks.json'
    return client.get(uri).json()['risks']


_cancellation_settings = {
    'cancel': {'cause_cancel': True, 'score': 1.0},
    'investigate': {'cause_cancel': False, 'score': 5.0},
    'accept': {'cause_cancel': False, 'score': 0.0}
    }


def _generate_risk_body(recommendation):
    settings = _cancellation_settings.get(recommendation)
    return {
        'risk': {
            'cause_cancel': settings['cause_cancel'],
            'message': 'FraudHooks recommendation',
            'recommendation': recommendation,
            'display': True,
            'source': 'External',
            'score': settings['score']
            }
        }


def create_order_risk(client, previous_risk, recommendation=None):
    if not recommendation:
        recommendation = 'cancel'
    new_risk = _generate_risk_body(recommendation)
    return client.post(f'{client.api_path}/orders/{previous_risk["order_id"]}/risks.json', json=new_risk)


def create_cancel_options():
    # TODO: only create restock options if there is an 
    # location_id on the line_item
    # https://shopify.dev/docs/admin-api/rest/reference/orders/refund?api[version]=2020-07
    pass


def cancel_order(client, order_number, options=None):
    uri = f'{client.api_path}/orders/{order_number}/cancel.json'
    return client.post(uri, json=options).json()


def get_fulfillment_orders(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/fulfillment_orders.json'
    return client.get(uri).json()['fulfillment_orders']


def get_fulfillment_order_id(fulfillment_orders, status=None):
    if not status:
        status = 'open'
    for fulfillment in fulfillment_orders:
        if fulfillment['status'] == status:
            return fulfillment['id']


def move_fulfillment_location(client, fulfillment_id, location_id):
    uri = f'{client.api_path}/fulfillment_orders/{fulfillment_id}/move.json'

    payload = {
            "fulfillment_order": {
                "new_location_id": location_id
                }
            }
    return client.post(uri, json=payload)


def get_shopify_page_link(response):
    link = response.headers.get('link')
    if link:
        for uri in link.split(','):
            if 'next' in uri:
                split = uri.split(';')[0][1:-1]
                if '<' not in split:
                    return split
                return uri.split(';')[0][2:-1]


def get_all_resources(client, initial_uri, resources=None, resource_type=None):
    if not resources:
        resources = []
    response = client.get(initial_uri)
    resources.extend(response.json()[resource_type])
    page_link = get_shopify_page_link(response)
    if page_link:
        get_all_resources(client, page_link, resources, resource_type)
    return resources


def get_all_resources_iter(client, initial_uri, resource_type=None):
    response = client.get(initial_uri)
    yield response.json()[resource_type]
    page_link = get_shopify_page_link(response)
    if page_link:
        yield from get_all_resources_iter(client, page_link, resource_type)


def execute_gql_query(client, query, variables=None):
    data = {'query': query,
            'variables': variables}

    return client.get(f'{client.gql_endpoint}', json=data)