import json
import urllib.request
import datetime
import re
from django.utils.timezone import get_fixed_timezone, utc
from .models import Registry
from django.utils import timezone
from django.shortcuts import get_object_or_404


data_url = 'http://ac.naks.ru/curl/json.php?url=reestr_personal&token=NtdRAUoEtsiwrew73UWyASw0wsYa&type=personal&popov=Y'


def date_parse(string):
    date_re = re.compile(
        r'(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>\d{4})$')
    match = date_re.match(string)
    if match:
        kw = {k: int(v) for k, v in match.groupdict().items()}
        return datetime.date(**kw)


class RegistryRecordAdapter:
    """adapter, that converts data to Registry model"""

    def __init__(self, args):
        self.created_date = date_parse(args['date_created'])
        self.title = args['title']
        self.org = args['org']
        self.typeof = args['typeof']
        self.params = args['params']
        self.status = args['status']


class RegistryRecordMapper:
    """relation between RegistryRecords objects and database"""

    def find_by(self, params, record):
        pass

    def check_if_exist(self, record):
        try:
            Registry.objects.get(title=record.title)
            print('Found')
            return True
        except Exception as e:
            print('Not found')
            return False

    def find_by_id(self, record):
        return get_object_or_404(Registry, pk=record.pk)

    def insert(self, record):
        try:
            record.save()
        except Exception as e:
            print(e)

    def update(self, id, **params):
        try:
            record = Registry.objects.get(pk=id)
            record.save(params)
        except Exception as e:
            print(e)

    def delete(self, record):
        try:
            rec = Registry.objects.get(pk=record.pk)
            rec.delete()
        except Exception as e:
            print(e)


class Importer:
    """importer, converter to json, and loader to database
        with checking if already loaded"""

    def __init__(self, url):
        self.data = self.get_data_from_url(url)
        self.mapper = RegistryRecordMapper()

    def get_data_from_url(self, url):
        data = urllib.request.urlopen(url)
        read_data = data.read()
        json_data = json.loads(read_data.decode('utf8'))
        return json_data

    def check_if_already_loaded(self, record):
        pass

    def save_data_to_db(self, record):
        """save every data record to DB using RegistryRecordAdapter"""
        args = {
            'date_created': record['date_create'],
            'title': record['fio']+'-'+record['vid_d']+'-'+record['stamp']+'-'+record['date_create'],
            'org': record['company'],
            'typeof': 'Аттестация персонала',
            'params': json.dumps(record),
            'status': 0
        }
        adapted_record = RegistryRecordAdapter(args)
        print(adapted_record.__dict__)
        record = Registry(**adapted_record.__dict__)
        if self.mapper.check_if_exist(record):
            """check if record already there"""
            print('Already there', record.title)
        else:
            """if not - insert with mapper method"""
            self.mapper.insert(record)
            print('SAVED NEW RECORD', record.title)
