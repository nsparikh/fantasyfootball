# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0007_auto_20141030_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='datapoint',
            name='dstYdsAllowed',
            field=models.IntegerField(null=True),
            preserve_default=True,
        ),
    ]
