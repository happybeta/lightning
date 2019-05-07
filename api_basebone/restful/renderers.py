import csv
import codecs
from collections import OrderedDict
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.writer.excel import save_virtual_workbook
from pydash import objects

from api_basebone.core import gmeta
from api_basebone.utils.gmeta import get_gmeta_config_by_key
from api_basebone.utils.timezone import local_timestamp


def get_fields(model):
    """获取导出的字段，显示名称的映射"""
    default_fields = OrderedDict()
    for item in model._meta.get_fields():
        if item.concrete and not item.many_to_many:
            default_fields[item.name] = item.verbose_name

    export_fields = get_gmeta_config_by_key(model, gmeta.GMETA_MANAGE_EXPORT_FIELDS)

    if not isinstance(export_fields, (list, tuple)) or not export_fields:
        return default_fields

    fields = OrderedDict()
    for item in export_fields:
        if isinstance(item, tuple):
            fields[item[0]] = item[1]
        else:
            fields[item] = default_fields[item]
    return fields


def row_data(fields, data):
    """获取每行的数据"""
    return [objects.get(data, key) for key in fields.keys()]


def row_with_relation_data(fields, reverse_field, object_id, data, relation_field_map):
    result = []

    data_map = {item['id']: item for item in data.get(reverse_field)}

    for key in fields.keys():
        if key in relation_field_map:
            result.append(objects.get(data_map[object_id], relation_field_map[key]))
        else:
            result.append(objects.get(data, key))
    return result


def csv_render(model, queryset, serializer_class):
    """渲染数据"""
    app_label, model_name = model._meta.app_label, model._meta.model_name
    file_name = f'{app_label}-{model_name}-{local_timestamp()}'

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'

    response.write(codecs.BOM_UTF8)

    fields = get_fields(model)
    verbose_names = fields.values()

    writer = csv.writer(response)
    writer.writerow(verbose_names)

    reverse_field = get_gmeta_config_by_key(model, gmeta.GMETA_MANAGE_REVERSE_FIELD)
    relation_field_map = get_gmeta_config_by_key(model, gmeta.GMETA_MANAGE_REVERSE_FIELDS_MAP)

    queryset_iter = queryset if isinstance(queryset, list) else queryset.iterator()
    for instance in queryset_iter:
        instance_data = serializer_class(instance).data
        if reverse_field:
            reverse_relation = getattr(instance, reverse_field, None)
            if not reverse_relation or not reverse_relation.count():
                writer.writerow(row_data(fields, instance_data))
            else:
                for r_item in reverse_relation.all().iterator():
                    writer.writerow(
                        row_with_relation_data(
                            fields, reverse_field, r_item.id, instance_data, relation_field_map
                        )
                    )
        else:
            writer.writerow(row_data(fields, instance_data))
    return response


class ExcelResponse(HttpResponse):
    def __init__(self, model, queryset, serializer_class, *args, **kwargs):
        self.model = model
        self.queryset = queryset
        self.serializer_class = serializer_class
        self.output_filename = f'{model._meta.model_name}.excel'
        self.worksheet_name = 'Sheet 1'

        super().__init__(model.objects.all(), *args, **kwargs)

    @property
    def content(self):
        return b''.join(self._container)

    @content.setter
    def content(self, value):
        self['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        self['Content-Disposition'] = 'attachment; filename={}.xlsx'.format(self.output_filename)

        workbook = self.build_excel()
        workbook = save_virtual_workbook(workbook)
        self._container = [self.make_bytes(workbook)]

    def build_excel(self, *args, **kwargs):
        fields = get_fields(self.model)
        headers = fields.values()

        workbook = Workbook(write_only=True)
        workbook.guess_types = True
        worksheet = workbook.create_sheet(title=self.worksheet_name)
        worksheet.append(headers)

        serializer_class = self.serializer_class
        for instance in self.queryset.iterator():
            instance_data = serializer_class(instance).data
            worksheet.append(row_data(fields, instance_data))
        return workbook
