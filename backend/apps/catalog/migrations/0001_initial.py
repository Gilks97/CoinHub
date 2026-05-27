from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CoinType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, db_index=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(unique=True)),
                ('conversion_rate', models.DecimalField(decimal_places=4, help_text='Coins per 1 KES. E.g. 10.0000 means 1 KES = 10 coins.', max_digits=18)),
                ('icon', models.ImageField(blank=True, null=True, upload_to='catalog/icons/')),
                ('active', models.BooleanField(db_index=True, default=True)),
            ],
            options={
                'verbose_name': 'Coin Type',
                'verbose_name_plural': 'Coin Types',
                'ordering': ['name'],
            },
        ),
    ]
