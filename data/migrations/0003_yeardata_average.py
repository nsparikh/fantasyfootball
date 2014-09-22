# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data', '0002_auto_20140922_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='yeardata',
            name='average',
            field=models.DecimalField(default=0, max_digits=5, decimal_places=1),
            preserve_default=True,
        ),
    ]
