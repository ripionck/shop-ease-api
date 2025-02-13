# Generated by Django 4.2.19 on 2025-02-13 12:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_category_options_alter_product_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='color',
            field=models.CharField(blank=True, choices=[('red', 'Red'), ('blue', 'Blue'), ('green', 'Green'), ('black', 'Black'), ('white', 'White'), ('custom', 'Custom')], max_length=50, null=True),
        ),
    ]
