
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


def cancel_order(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/cancel.json'
    return client.post(uri).json()


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
