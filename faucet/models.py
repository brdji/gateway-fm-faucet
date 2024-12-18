from django.db import models


class FaucetRequest(models.Model):
    destination_address = models.CharField(max_length=42)
    ip_address = models.CharField(max_length=50)
    tx_hash = models.CharField(default="", max_length=66)
    created_on = models.DateTimeField(auto_now_add=True)
