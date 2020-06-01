
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

def get_all_resources_recursive(client, page_link,
                                resource_type=None,
                                resources=None):
    if not resources:
        resources = []
    response = client.get(page_link)
    if not resource_type:
        raise ValueError('please provide a resource type')
    resources.extend(response.json()[resource_type])
    order_link = get_shopify_page_link(response)
    if order_link:
        get_all_resources_recursive(client, page_link, resources)
    return resources

def pass_verification_pipeline(funcs_to_apply, resource):
    for func in funcs_to_apply:
        if not func(resource):
            return False
    return True
