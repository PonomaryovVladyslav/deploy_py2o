# Generated by Django 4.1.3 on 2022-11-14 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0005_alter_purchase_options_alter_purchase_quantity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='purchase',
            name='quantity',
            field=models.PositiveSmallIntegerField(),
        ),
    ]