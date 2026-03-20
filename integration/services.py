import requests

COUNTRY_API = "https://restcountries.com/v3.1/name/{}"
EXCHANGE_API = "https://api.exchangerate-api.com/v4/latest/USD"

def get_country_data(country_name):
    response = requests.get(COUNTRY_API.format(country_name), timeout=5)
    if response.status_code != 200:
        return None
    data = response.json()[0]
    currencies = data.get("currencies", {})
    currency_code = list(currencies.keys())[0]
    currency_name = currencies[currency_code]["name"]
    return {
        "country": data["name"]["common"],
        "capital": data["capital"][0] if data.get("capital") else "N/A",
        "region": data.get("region", "N/A"),
        "population": data.get("population", 0),
        "currency_code": currency_code,
        "currency_name": currency_name,
    }

def get_exchange_rate(currency_code):
    response = requests.get(EXCHANGE_API, timeout=5)
    if response.status_code != 200:
        return None
    rates = response.json().get("rates", {})
    return rates.get(currency_code)

def get_unified_data(country_name):
    country = get_country_data(country_name)
    if not country:
        return None, "country_not_found"

    rate = get_exchange_rate(country["currency_code"])
    if rate is None:
        return None, "exchange_not_found"

    country["exchange_rate_to_usd"] = rate
    country["usd_to_currency"] = f"1 USD = {rate} {country['currency_code']}"
    return country, None