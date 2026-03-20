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



views.py
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .services import get_unified_data
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CountryCurrencySummaryView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'country', openapi.IN_QUERY,
                description="Name of the country (e.g. Japan)",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={
            200: "Unified country + currency data",
            400: "Missing country parameter",
            404: "Country or currency not found",
            502: "External API failure",
        }
    )
    def get(self, request):
        country_name = request.query_params.get("country", "").strip()

        if not country_name:
            return Response(
                {"error": "Missing required parameter: country"},
                status=status.HTTP_400_BAD_REQUEST
            )

        data, error = get_unified_data(country_name)

        if error == "country_not_found":
            return Response(
                {"error": f"Country '{country_name}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        if error == "exchange_not_found":
            return Response(
                {"error": "Exchange rate data unavailable."},
                status=status.HTTP_502_BAD_GATEWAY
            )

        return Response(data, status=status.HTTP_200_OK)

tests.py
from django.test import TestCase
from django.test import TestCase
from unittest.mock import patch
from django.urls import reverse

class CountryCurrencyTest(TestCase):

    @patch('integration.services.get_country_data')
    @patch('integration.services.get_exchange_rate')
    def test_successful_response(self, mock_rate, mock_country):
        mock_country.return_value = {
            "country": "Japan",
            "capital": "Tokyo",
            "region": "Asia",
            "population": 125700000,
            "currency_code": "JPY",
            "currency_name": "Japanese Yen",
        }
        mock_rate.return_value = 149.50

        response = self.client.get('/api/v1/country-currency-summary/?country=Japan')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['country'], 'Japan')
        self.assertIn('exchange_rate_to_usd', response.data)

    def test_missing_country_param(self):
        response = self.client.get('/api/v1/country-currency-summary/')
        self.assertEqual(response.status_code, 400)
