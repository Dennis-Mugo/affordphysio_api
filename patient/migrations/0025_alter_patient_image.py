# Generated by Django 4.2.15 on 2024-09-05 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0024_patient_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='patient',
            name='image',
            field=models.ImageField(null=True, upload_to='assets/patient_images/'),
        ),
    ]
