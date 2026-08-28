from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salons', '0010_subscriptiontransaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='salonpublication',
            name='media',
            field=models.ImageField(blank=True, null=True, upload_to='publications/'),
        ),
    ]
