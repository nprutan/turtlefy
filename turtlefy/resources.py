
def cancel_order(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/cancel.json'
    return client.post(uri).json()


def get_shopify_page_link(response):
    link = response.headers.get('link')
    if link:
        for uri in link.split(','):
            if 'next' in uri:
                split = uri.split(';')[0][1:-1]
                if '<' not in split:
                    return split
                return uri.split(';')[0][2:-1]


def get_all_resources(client, initial_uri,
                      resources=None,
                      resource_type=None):
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


