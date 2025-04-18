# Generated by Django 5.2 on 2025-04-02 19:33

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('artworks', '0002_initial'),
        ('events', '0002_initial'),
        ('live_streams', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='livestream',
            name='artist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='live_streams', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='livestream',
            name='artwork',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='live_streams', to='artworks.artwork'),
        ),
        migrations.AddField(
            model_name='livestream',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='live_streams', to='events.event'),
        ),
    ]
