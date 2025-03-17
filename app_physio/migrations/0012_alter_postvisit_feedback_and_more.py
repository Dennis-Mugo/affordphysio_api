# Generated by Django 5.0.4 on 2025-03-17 08:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_physio', '0011_alter_postvisit_follow_up_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='postvisit',
            name='feedback',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='postvisit',
            name='pain_management',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='postvisit',
            name='recommendations',
            field=models.TextField(null=True),
        ),
        migrations.AlterField(
            model_name='postvisit',
            name='treatment_plan',
            field=models.TextField(null=True),
        ),
    ]
