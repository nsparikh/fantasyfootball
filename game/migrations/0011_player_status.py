# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0010_auto_20140922_1411'),
    ]

    operations = [
        migrations.AddField(
            model_name='player',
            name='status',
            field=models.CharField(max_length=200, null=True),
            preserve_default=True,
        ),
    ]
