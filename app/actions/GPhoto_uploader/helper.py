from zendriver import Browser
from zendriver.cdp import network


async def get_response(tab, url) -> int:

    await tab.send(network.enable())

    response_codes: dict[str, int] = {}
    # Add a handler for ResponseReceived events
    tab.add_handler(
        network.ResponseReceived,
        lambda e: (
            response_codes.update({e.response.url: e.response.status})
            if e.response.url == url
            else None
        ),
    )
    await tab.get(url)
    await tab.send(network.disable())
    return response_codes[url]
