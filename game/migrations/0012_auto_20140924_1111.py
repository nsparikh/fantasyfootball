# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0011_player_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='position',
            name='average',
        ),
        migrations.RemoveField(
            model_name='position',
            name='average1',
        ),
        migrations.RemoveField(
            model_name='position',
            name='average2',
        ),
        migrations.RemoveField(
            model_name='position',
            name='average3',
        ),
        migrations.RemoveField(
            model_name='position',
            name='average4',
        ),
    ]
