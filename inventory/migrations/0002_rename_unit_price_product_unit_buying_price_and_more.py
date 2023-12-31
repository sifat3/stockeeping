# Generated by Django 4.1.5 on 2023-09-26 20:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='unit_price',
            new_name='unit_buying_price',
        ),
        migrations.RemoveField(
            model_name='purchase',
            name='purchase_price',
        ),
        migrations.RemoveField(
            model_name='sale',
            name='sale_price',
        ),
        migrations.AddField(
            model_name='product',
            name='unit_selling_price',
            field=models.DecimalField(decimal_places=2, default=22, max_digits=10),
            preserve_default=False,
        ),
    ]
