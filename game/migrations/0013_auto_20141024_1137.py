# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0012_auto_20140924_1111'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='yahoo_id',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='player',
            name='espn_id',
            field=models.IntegerField(null=True),
        ),
    ]
