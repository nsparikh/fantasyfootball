# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0005_gamedata_performance_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='bonus40YdPassTDs',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='bonus40YdRecTDs',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='bonus40YdRushTDs',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
