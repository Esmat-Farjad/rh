# Generated by Django 4.0.6 on 2023-11-19 04:53

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("stock", "0005_alter_stocklocationdetails_options_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="stocktype",
            name="countries",
        ),
    ]
