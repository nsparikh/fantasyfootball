# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0007_auto_20140922_1046'),
    ]

    operations = [
        migrations.AlterField(
            model_name='matchup',
            name='bye',
            field=models.NullBooleanField(default=None),
        ),
        migrations.AlterField(
            model_name='matchup',
            name='win',
            field=models.NullBooleanField(default=None),
        ),
    ]
