
def extract_tags(tags):
    return [tag.strip().lower() for tag in tags.split(',')]


def append_tags(tags, new_tag):
    if tags:
        split_tags = tags.split(',')
        split_tags.append(f' {new_tag}')
        return ','.join(split_tags)
    return new_tag


def tag_customer(client, customer, new_tag):
    customer_id = int(customer['id'])
    updated_tags = append_tags(customer['tags'], new_tag)
    tag_data = {
        "customer": {
            "id": customer_id,
            "tags": updated_tags
        }
    }
    url = f'{client.api_path}/customers/{customer_id}.json'
    return client.put(url, json=tag_data).status_code


def get_customer_by_id(client, customer_id):
    return client.get(f'{client.api_path}/customers/{customer_id}.json').json()['customer']


def get_order_by_id(client, order_id):
    return client.get(f'{client.api_path}/orders/{order_id}.json').json()['order']


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


def get_transactions(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/transactions.json'
    return client.get(uri).json()['transactions']


def get_fulfillment_orders(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/fulfillment_orders.json'
    return client.get(uri).json()['fulfillment_orders']


def _generate_refund_line_items(fulfillments, restock_type):
    return [
        {
            'line_item_id': line['line_item_id'],
            'quantity': line['quantity'],
            'restock_type': restock_type,
            'location_id': fulfillment['assigned_location_id']
        } for fulfillment in fulfillments for line in fulfillment['line_items']
    ]


def _generate_refund_transactions(transactions):
    return [
        {
            'parent_id': tx['parent_id'],
            'amount': tx['amount'],
            'kind': 'refund',
            'gateway': tx['gateway']
        } for tx in transactions if tx['parent_id']
    ]


def create_refund(transactions, fulfillments, restock_type='cancel'):
    return {
        "refund": {
            "note": "FraudHooks Cancellation",
            "shipping": {
            "full_refund": True
            },
            "refund_line_items": _generate_refund_line_items(fulfillments, restock_type),
            "transactions": _generate_refund_transactions(transactions)
        }
    }


def get_order_risks(client, order_number):
    uri = f'{client.api_path}/orders/{order_number}/risks.json'
    return client.get(uri).json()['risks']


_cancellation_settings = {
    'cancel': {'cause_cancel': True, 'score': 1.0},
    'investigate': {'cause_cancel': False, 'score': 0.5},
    'accept': {'cause_cancel': False, 'score': 0.0}
    }


def _generate_risk_body(recommendation, message):
    settings = _cancellation_settings.get(recommendation)
    if not message:
        message = 'Order determined to be high risk'
    return {
        'risk': {
            'cause_cancel': settings['cause_cancel'],
            'message': message,
            'recommendation': recommendation,
            'display': True,
            'source': 'External',
            'score': settings['score']
            }
        }


def create_order_risk(client, previous_risk, recommendation=None, message=None):
    if not recommendation:
        recommendation = 'cancel'
    new_risk = _generate_risk_body(recommendation, message)
    return client.post(f'{client.api_path}/orders/{previous_risk["order_id"]}/risks.json', json=new_risk)


def create_cancel_options(options):
    refund = {}
    if options['refund']:
        restock_type = 'no_restock' if not options['restock'] else 'cancel'
        refund = create_refund(options['transactions'], options['fulfillments'], restock_type=restock_type)
    return {
        **refund,
        'email': options['notify_customer'],
        'reason': 'fraud'
    }


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


def execute_gql_query(client, query):
        client.update_gql_headers()
        return client.post(f'{client.gql_endpoint}', data=query)

        