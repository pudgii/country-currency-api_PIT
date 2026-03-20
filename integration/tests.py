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
