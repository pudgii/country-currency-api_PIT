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
