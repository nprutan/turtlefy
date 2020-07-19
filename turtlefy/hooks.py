import time

def calculate_wait_time(r):
    leak = r.headers.get('X-Shopify-Shop-Api-Call-Limit', None)
    if leak:
        count = int(leak.split('/')[0])
        if count > 35:
            return count / 2
    return 0


# TODO: Implement expo backoff with https://github.com/litl/backoff
def handle_shopify_rate_limit(r, *args, **kwargs):
    wait = calculate_wait_time(r)
    if wait:
        print(f'leak rate: {r.headers.get("X-Shopify-Shop-Api-Call-Limit", None)}')
        print(f'sleeping for: {wait} seconds...')
        time.sleep(wait)
    return r
