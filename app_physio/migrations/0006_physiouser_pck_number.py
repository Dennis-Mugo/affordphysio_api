# Generated by Django 5.0.4 on 2024-06-27 05:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_physio', '0005_postvisit'),
    ]

    operations = [
        migrations.AddField(
            model_name='physiouser',
            name='pck_number',
            field=models.IntegerField(null=True),
        ),
    ]
