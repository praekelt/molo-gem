# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-10-16 13:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('profiles', '0008_change_num_security_questions_default'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityQuestionIndexPage',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'abstract': False,
            },
            bases=('wagtailcore.page',),
        ),
        migrations.AlterModelOptions(
            name='securityquestion',
            options={'verbose_name': 'Security Question'},
        ),
        migrations.RemoveField(
            model_name='securityquestion',
            name='id',
        ),
        migrations.RemoveField(
            model_name='securityquestion',
            name='question',
        ),
        migrations.AddField(
            model_name='securityquestion',
            name='page_ptr',
            field=models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page'),
            preserve_default=False,
        ),
    ]