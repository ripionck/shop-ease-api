# Generated by Django 4.2.19 on 2025-02-13 22:19

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0007_alter_productimage_image'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Review',
        ),
    ]
