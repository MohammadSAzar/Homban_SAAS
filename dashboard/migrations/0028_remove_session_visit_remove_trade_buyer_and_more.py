# Generated by Django 5.1.7 on 2025-05-25 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0027_person_status_renter_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='session',
            name='visit',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='buyer',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='customer_national_code',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='owner',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='owner_national_code',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='renter',
        ),
        migrations.RemoveField(
            model_name='trade',
            name='session',
        ),
        migrations.RemoveField(
            model_name='visit',
            name='customer',
        ),
        migrations.RemoveField(
            model_name='visit',
            name='rent_file',
        ),
        migrations.RemoveField(
            model_name='visit',
            name='sale_file',
        ),
        migrations.AddField(
            model_name='session',
            name='buyer_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Buyer Code'),
        ),
        migrations.AddField(
            model_name='session',
            name='rent_file_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Rent File Code'),
        ),
        migrations.AddField(
            model_name='session',
            name='renter_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Renter Code'),
        ),
        migrations.AddField(
            model_name='session',
            name='sale_file_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Sale File Code'),
        ),
        migrations.AddField(
            model_name='session',
            name='visit_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Visit Code'),
        ),
        migrations.AddField(
            model_name='trade',
            name='contract_buyer',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Contract Customer (Buyer)'),
        ),
        migrations.AddField(
            model_name='trade',
            name='contract_owner',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='Contract Owner (Seller / Lessor)'),
        ),
        migrations.AddField(
            model_name='trade',
            name='contract_renter',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='Contract Customer (Renter)'),
        ),
        migrations.AddField(
            model_name='trade',
            name='session_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Session Code'),
        ),
        migrations.AddField(
            model_name='visit',
            name='buyer_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Buyer Code'),
        ),
        migrations.AddField(
            model_name='visit',
            name='rent_file_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Rent File Code'),
        ),
        migrations.AddField(
            model_name='visit',
            name='renter_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Renter Code'),
        ),
        migrations.AddField(
            model_name='visit',
            name='sale_file_code',
            field=models.CharField(blank=True, max_length=6, null=True, unique=True, verbose_name='Sale File Code'),
        ),
    ]
