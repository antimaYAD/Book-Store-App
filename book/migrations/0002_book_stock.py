# Generated by Django 5.1.1 on 2024-09-24 05:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="book",
            name="stock",
            field=models.IntegerField(default=0),
        ),
    ]
