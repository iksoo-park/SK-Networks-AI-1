# Generated by Django 5.0.6 on 2024-06-11 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("product", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="product",
            old_name="registeredDate",
            new_name="resisteredDate",
        ),
    ]
