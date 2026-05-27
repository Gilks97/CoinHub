import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('checkout_request_id', models.CharField(blank=True, db_index=True, max_length=100)),
                ('merchant_request_id', models.CharField(blank=True, max_length=100)),
                ('mpesa_receipt', models.CharField(blank=True, db_index=True, max_length=50)),
                ('phone_number', models.CharField(max_length=20)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('status', models.CharField(
                    choices=[('pending','Pending'),('success','Success'),('failed','Failed'),('cancelled','Cancelled')],
                    db_index=True, default='pending', max_length=20)),
                ('raw_callback_json', models.JSONField(blank=True, null=True)),
                ('order', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE,
                    related_name='payment', to='orders.order')),
            ],
            options={
                'verbose_name': 'Payment',
                'verbose_name_plural': 'Payments',
                'ordering': ['-created_at'],
            },
        ),
    ]
