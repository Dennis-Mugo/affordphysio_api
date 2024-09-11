# Generated by Django 4.2.15 on 2024-09-11 06:14

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('app_physio', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('status', models.CharField(max_length=50)),
                ('appointment_type', models.CharField(max_length=50)),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('amount', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('id_number', models.CharField(max_length=50, null=True)),
                ('date_of_birth', models.DateTimeField(null=True)),
                ('gender', models.CharField(max_length=50, null=True)),
                ('weight', models.IntegerField(null=True)),
                ('height', models.IntegerField(null=True)),
                ('phone_number', models.CharField(max_length=15)),
                ('marital_status', models.CharField(max_length=30, null=True)),
                ('religion', models.CharField(max_length=50, null=True)),
                ('education', models.TextField(null=True)),
                ('occupation', models.CharField(max_length=50, null=True)),
                ('chronic_disease_history', models.TextField(null=True)),
                ('hobby', models.CharField(max_length=50, null=True)),
                ('image', models.ImageField(null=True, upload_to='assets/patient_images/')),
                ('reset_code', models.CharField(max_length=10, null=True)),
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
        migrations.CreateModel(
            name='Penalty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('penalty_type', models.CharField(max_length=50, null=True)),
                ('fine_percentage', models.IntegerField(null=True)),
                ('duration', models.BigIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, null=True)),
                ('status', models.CharField(max_length=50, null=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.appointment')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
        migrations.CreateModel(
            name='PatientLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(null=True)),
                ('activity', models.CharField(max_length=50, null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
            ],
        ),
        migrations.CreateModel(
            name='PatientFeedback',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(null=True)),
                ('comments', models.TextField(null=True)),
                ('rating', models.IntegerField(null=True)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient')),
                ('physiotherapist', models.ForeignKey(default=24, on_delete=django.db.models.deletion.CASCADE, to='app_physio.physiouser')),
            ],
        ),
        migrations.CreateModel(
            name='AppointmentCancellation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(null=True)),
                ('reason', models.TextField(null=True)),
                ('appointment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.appointment')),
                ('penalty', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='patient.penalty')),
            ],
        ),
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patient.patient'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='physiotherapist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_physio.physiouser'),
        ),
    ]
