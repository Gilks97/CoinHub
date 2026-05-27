import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("catalog", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('reference', models.CharField(db_index=True, max_length=20, unique=True)),
                ('app_user_id', models.CharField(help_text='External game/app user identifier', max_length=100)),
                ('phone_number', models.CharField(help_text='M-Pesa phone in 2547XXXXXXXX format', max_length=20)),
                ('coins_requested', models.PositiveIntegerField()),
                ('amount_paid', models.DecimalField(decimal_places=2, help_text='Amount in KES', max_digits=12)),
                ('status', models.CharField(
                    choices=[('pending','Pending'),('paid','Paid'),('loaded','Loaded'),('failed','Failed')],
                    db_index=True, default='pending', max_length=20)),
                ('loaded_at', models.DateTimeField(blank=True, null=True)),
                ('loading_notes', models.TextField(blank=True)),
                ('coin_type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT,
                    related_name='orders', to='catalog.cointype')),
                ('loaded_by', models.ForeignKey(blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='loaded_orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Order',
                'verbose_name_plural': 'Orders',
                'ordering': ['-created_at'],
            },
        ),
    ]
