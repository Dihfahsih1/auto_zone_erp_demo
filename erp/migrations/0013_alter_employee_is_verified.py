# Generated by Django 4.1.13 on 2025-04-23 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erp', '0012_rename_address_employee_is_verified'),
    ]

    operations = [
        migrations.AlterField(
            model_name='employee',
            name='is_verified',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='Verified by Admin'),
        ),
    ]
