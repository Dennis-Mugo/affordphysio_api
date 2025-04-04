# Generated by Django 5.0.4 on 2024-04-20 12:40

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_admin', '0005_alter_adminuser_years_of_experience'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailToken',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
