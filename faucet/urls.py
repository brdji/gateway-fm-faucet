from django.urls import path
from . import views

app_name = "faucet"
urlpatterns = [
    path("fund", views.faucet_fund, name="faucet_fund"),
    path("stats", views.list_fund_stats, name="faucet_stats"),
]
