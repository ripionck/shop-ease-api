# Generated by Django 4.2.19 on 2025-03-12 19:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('orders', '0005_remove_order_payment_method'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(choices=[('card', 'Credit/Debit Card'), ('bank_transfer', 'Bank Transfer'), ('wallet', 'Digital Wallet')], default='card', max_length=20)),
                ('transaction_id', models.CharField(blank=True, max_length=255, null=True, unique=True)),
                ('stripe_payment_intent_id', models.CharField(blank=True, max_length=255, null=True)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('requires_payment_method', 'Requires Payment Method'), ('requires_confirmation', 'Requires Confirmation'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed'), ('canceled', 'Canceled')], default='pending', max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payments', to='orders.order')),
            ],
        ),
    ]
