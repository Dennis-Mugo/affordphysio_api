# Generated by Django 5.0.4 on 2024-06-23 13:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_physio', '0004_physioschedule'),
    ]

    operations = [
        migrations.CreateModel(
            name='PostVisit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('patient', models.IntegerField()),
                ('treatment_plan', models.TextField()),
                ('recommendations', models.TextField()),
                ('follow_up_date', models.DateField()),
                ('pain_management', models.TextField()),
                ('feedback', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('physio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_physio.physiouser')),
            ],
        ),
    ]
