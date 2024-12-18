# Generated by Django 5.1.4 on 2024-12-18 10:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="FaucetRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("destination_address", models.CharField(max_length=42)),
                ("ip_address", models.CharField(max_length=50)),
                ("tx_hash", models.CharField(default="", max_length=66)),
                ("created_on", models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
