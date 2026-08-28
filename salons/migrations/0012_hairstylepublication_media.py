from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('salons', '0011_salonpublication_media'),
    ]

    operations = [
        migrations.AddField(
            model_name='hairstylepublication',
            name='media',
            field=models.ImageField(blank=True, null=True, upload_to='hairstyles/'),
        ),
    ]
