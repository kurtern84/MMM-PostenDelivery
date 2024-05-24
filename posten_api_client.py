import asyncio
import base64
import time
import socket
import aiohttp
import json
import sys
from datetime import datetime, timedelta
from typing import Optional

TIMEOUT = 10

class PostenApiError(Exception):
    """Posten API error."""

class IntegrationPostenApiClient:
    """Posten API Client."""

    def __init__(self, postalcode: str, session: aiohttp.ClientSession) -> None:
        """Posten API Client."""
        self._session = session
        self._postalcode = postalcode

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        return await self.api_wrapper(
            method="get",
            url=f"https://www.posten.no/levering-av-post/_/service/no.posten.website/delivery-days?postalCode={self._postalcode}",
            headers={
                "content-type": "application/json; charset=UTF-8",
                "x-requested-with": "XMLHttpRequest",
                "kp-api-token": base64.b64encode(
                    bytes(base64.b64decode("f3ccd044MTY4MjYyODE2MQ==")[0:6])
                    + bytes(str(int(time.time())), "utf8")
                ).decode().replace("=", ""),
            },
        )

    async def api_wrapper(self, method: str, url: str, headers: Optional[dict] = None) -> dict:
        """Get information from the API."""
        try:
            response = await self._session.request(
                method,
                url,
                headers=headers or {},
                timeout=aiohttp.ClientTimeout(total=TIMEOUT),
            )
            return await response.json()
        except asyncio.TimeoutError as exception:
            raise PostenApiError(f"Timeout error fetching information from {url}") from exception
        except (KeyError, TypeError) as exception:
            raise PostenApiError(f"Error parsing information from {url} - {exception}") from exception
        except (aiohttp.ClientError, socket.gaierror) as exception:
            raise PostenApiError(f"Error fetching information from {url}") from exception
        except Exception as exception:
            raise PostenApiError(f"Something really wrong happened! - {exception}") from exception

async def main():
    postalcode = sys.argv[1]
    async with aiohttp.ClientSession() as session:
        client = IntegrationPostenApiClient(postalcode, session)
        try:
            data = await client.async_get_data()
            delivery_dates = data.get('delivery_dates', [])
            today = datetime.now().date()

            if not delivery_dates:
                print(json.dumps({"error": "No delivery dates found"}))
                return

            next_delivery_date = None
            for date_str in delivery_dates:
                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                if date >= today:
                    next_delivery_date = date
                    break

            if next_delivery_date is None:
                print(json.dumps({"error": "No upcoming delivery dates"}))
                return

            days_diff = (next_delivery_date - today).days

            if days_diff == 0:
                delivery_text = "i dag"
            elif days_diff == 1:
                delivery_text = "i morgen"
            else:
                delivery_text = f"om {days_diff} dager"

            print(json.dumps({"next_delivery": delivery_text}))

        except PostenApiError as e:
            print(json.dumps({"error": str(e)}))

if __name__ == "__main__":
    asyncio.run(main())
