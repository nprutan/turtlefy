# turtlefy
```
              _,.---.---.---.--.._
            _.-' `--.`---.`---'-. _,`--.._
           /`--._ .'.     `.     `,`-.`-._\
          ||   \  `.`---.__`__..-`. ,'`-._/
     _  ,`\ `-._\   \    `.    `_.-`-._,``-.
  ,`   `-_ \/ `-.`--.\    _\_.-'\__.-`-.`-._`.
 (_.o> ,--. `._/'--.-`,--`  \_.-'       \`-._ \
  `---'    `._ `---._/__,----`           `-. `-\
            /_, ,  _..-'                    `-._\
            \_, \/ ._(
             \_, \/ ._\
              `._,\/ ._\
                `._// ./`-._
                  `-._-_-_.-'
```

A collection of Shopify utilities to make life easier.

Sometimes you just want to get things done in a straightforward
and lightweight manner.

Like pulling all your Shopify orders into a list so you
can do stuff with them.

Instead of reading all the API docs on how to paginate your
orders, or customers, products etc, just use the recursive
function and you've got your list. Now do stuff.

## Usage:

```python
from turtlefy.client import get_turtlefy_client
from turtlefy.resources import get_all_resources

client = get_turtlefy_client('https://base.myshopify.com', token='xxxx')

order_uri = f'{client.api_path}/orders.json'

orders = get_all_resources(client, order_uri, resource_type='orders')

len(orders) >> 50
```

In addition, you can use the get_all_resources_iter function like this:

```python
from turtlefy.resources import get_all_resources_iter

# Note that using limit=1 is very inefficient, but you can
# yield one resource at a time this way
customer_uri = f'{client.api_path}/customers.json?limit=1'

for customer in get_all_resources_iter(client, customer_uri, resource_type='customer'):
    print(customer)

order_uri = f'{client.api_path}/orders.json?limit=250'

for orders in get_all_resources_iter(client, order_uri, resource_type='orders'):
    print(f'Got {len(orders)} orders')

```

## Automatic Rate Limiting:

Also, some little goodies include automatic rate limit detection.
Shopify uses a "leaky bucket algorithm" to determine when to start
rate limiting your requests.

https://shopify.dev/concepts/about-apis/rate-limits

Normally you would need to write some detection and backoff code in order to
pull a bunch of resources without hitting limits. With the Turtlefy client you
can just get all the resources and the client will handle the rate limit
backoff.

NOTE: Currently this uses a very naive halving of the bucket leak
count. This will be getting a better, and proper exponential backoff
capability in the near future.

What's with the name? It's turtles all the way down!

https://en.m.wikipedia.org/wiki/Turtles_all_the_way_down

