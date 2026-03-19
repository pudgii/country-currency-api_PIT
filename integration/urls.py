from django.urls import path
from .views import CountryCurrencySummaryView

urlpatterns = [
    path('country-currency-summary/', CountryCurrencySummaryView.as_view()),
]