# Generated by Django 4.2.15 on 2024-09-09 07:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0026_alter_patient_phone_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='reset_code',
            field=models.CharField(max_length=10, null=True),
        ),
    ]
