# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0002_player_depth_position'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='division',
            field=models.CharField(max_length=200, null=True),
            preserve_default=True,
        ),
    ]
