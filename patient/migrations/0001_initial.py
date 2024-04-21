# Generated by Django 5.0.4 on 2024-04-21 10:04

import django.contrib.auth.models
import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, to=settings.AUTH_USER_MODEL)),
                ('patientId', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('id_number', models.CharField(max_length=50, null=True)),
                ('date_of_birth', models.DateTimeField(null=True)),
                ('gender', models.CharField(max_length=50, null=True)),
                ('weight', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('phone_number', models.CharField(max_length=15, null=True)),
                ('marital_status', models.CharField(max_length=30, null=True)),
                ('religion', models.CharField(max_length=50, null=True)),
                ('education', models.TextField(null=True)),
                ('chronic_disease_history', models.TextField(null=True)),
                ('occupation', models.CharField(max_length=50, null=True)),
                ('hobby', models.CharField(max_length=50, null=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
    ]
