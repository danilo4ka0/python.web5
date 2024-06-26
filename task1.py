import aiohttp
import asyncio
import sys
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class ExchangeRateClient:
    def __init__(self, days):
        self.days = days
        self.base_url = API_URL

    async def fetch_exchange_rate(self, session, date):
        url = f"{self.base_url}{date}"
        try:
            async with session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientError as e:
            print(f"Error fetching data for {date}: {e}")
            return None

    async def get_exchange_rates(self):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(self.days):
                date = (datetime.now() - timedelta(days=i)).strftime('%d.%m.%Y')
                tasks.append(self.fetch_exchange_rate(session, date))
            return await asyncio.gather(*tasks)


def format_data(raw_data):
    result = []
    for data in raw_data:
        if not data:
            continue
        date = data['date']
        rates = {
            'EUR': None,
            'USD': None
        }
        for rate in data['exchangeRate']:
            if rate['currency'] in rates:
                rates[rate['currency']] = {
                    'sale': rate.get('saleRate', 'N/A'),
                    'purchase': rate.get('purchaseRate', 'N/A')
                }
        result.append({date: rates})
    return result


class ExchangeRateService:
    def __init__(self, client):
        self.client = client

    async def get_rates(self):
        raw_data = await self.client.get_exchange_rates()
        return format_data(raw_data)


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        return

    try:
        days = int(sys.argv[1])
    except ValueError:
        print("Please provide a valid number for the number of days.")
        return

    if days > 10:
        print("Please provide a number of days not more than 10.")
        return

    client = ExchangeRateClient(days)
    service = ExchangeRateService(client)

    rates = asyncio.run(service.get_rates())
    print(rates)


if __name__ == "__main__":
    main()
