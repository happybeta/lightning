# Generated by Django 2.2.9 on 2020-07-22 23:08

from django.db import migrations
import jsonfield.fields
from django.conf import settings as SETTINGS
import json

def update_value_jsonfield(apps, schema_editor):
    print('更新update_value_jsonfield')
    Setting = apps.get_app_config('bsm_config').get_model('Setting')
    all_fields = {}
    if getattr(SETTINGS, 'WEBSITE_CONFIG', None):
        for section in SETTINGS.WEBSITE_CONFIG:
            for field in section['fields']:
                all_fields[field['name']] = field
    settings = Setting.objects.all()
    updata_settings = []
    for setting in settings:
        if setting.value or (setting.value_json and setting.value_json.get('value',None)):
            type = all_fields.get(setting.key,{}).get('type','string')
            value = setting.value
            if setting.value_json and setting.value_json.get('value',None):
                value = setting.value_json.get('value',None)
            if type == 'string':
                value = json.dumps(value)
            if type == 'bool':
                bool_mapping = {'True': json.dumps(True), 'False': json.dumps(False) }
                value = bool_mapping[value]
            setting.value = value
            updata_settings.append(setting)
    Setting.objects.bulk_update(updata_settings, ['value'])

def reverse_update_value_jsonfield(apps, schema_editor):
    print('回退')
    Setting = apps.get_app_config('bsm_config').get_model('Setting')
    updata_settings = []
    for setting  in Setting.objects.all():
        if setting.value != None:
            setting.value = json.loads(setting.value)
            updata_settings.append(setting)
    Setting.objects.bulk_update(updata_settings, ['value'])

class Migration(migrations.Migration):

    dependencies = [
        ('bsm_config', '0025_auto_20200716_2253'),
    ]

    operations = [
        migrations.RunPython(update_value_jsonfield, reverse_code=reverse_update_value_jsonfield),
        migrations.RemoveField(
            model_name='setting',
            name='groups',
        ),
        migrations.RemoveField(
            model_name='setting',
            name='value_json',
        ),
        migrations.AlterField(
            model_name='setting',
            name='value',
            field=jsonfield.fields.JSONField(null=True, verbose_name='配置值'),
        )
    ]