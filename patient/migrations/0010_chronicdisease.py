# Generated by Django 5.0.4 on 2024-05-03 07:23

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0009_remove_patient_chronic_disease_history'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChronicDisease',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disease', models.CharField(max_length=150, null=True)),
                ('patient', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
    ]
