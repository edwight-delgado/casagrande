# Generated by Django 4.1.7 on 2023-03-20 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="note",
            field=models.CharField(blank=True, max_length=150, null=True),
        ),
    ]
