# turtlefy
A collection of Shopify utilities to make life easier.


Sometimes you just want to get things done in a straightforward
and lightweight manner.

Like pulling all your Shopify orders into a list so you
can do stuff with them.

Instead of reading all the API docs on how to paginate your
orders, or customers, products etc, just use the recursive
function and you've got your list. Now do stuff.

EXAMPLE:

```python
from client import get_turtlefy_client
from resources import get_all_resources_recursive

client = get_turtlefy_client('https://base.myshopify.com', token='xxxx')

order_uri = f'{client.api_path}/orders.json'

orders = get_all_resources_recursive(client, order_uri, resource_type='orders')

len(orders) >> 50
```

What's with the name? It's turtles all the way down!

https://en.m.wikipedia.org/wiki/Turtles_all_the_way_down

