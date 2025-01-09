from zendriver import Browser


async def main():
    # Initialize Zendriver
    async with Browser() as driver:
        # Enable the Network domain
        await driver.cdp.Network.enable()

        # Define a callback to capture response events
        async def capture_response(event):
            response = event.get("response", {})
            url = response.get("url")
            status_code = response.get("status")
            print(f"URL: {url}, Status Code: {status_code}")

        # Subscribe to the Network.responseReceived event
        driver.cdp.Network.responseReceived = capture_response

        # Navigate to a URL
        await driver.get("https://google.com")


# Run the async function
import asyncio

asyncio.run(main())
