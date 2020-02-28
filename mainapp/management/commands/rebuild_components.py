from django.core.management.base import BaseCommand
from mainapp.models import Component
from mainapp.models import ComponentParameter
from django.core.files import File
from django.conf import settings
import json
import os
import shutil
import time
from django.utils.termcolors import colorize

from .install_components import COMPONENTS_FOLDER, SCSS_FOLDER


class Command(BaseCommand):
    def read_installed_lock(self, path_to_file):
        with open(path_to_file, 'r') as lock_file:
            component_data = lock_file.read()
            component_json = json.loads(component_data)


    def handle(self, *args, **options):
        components_root_folder = COMPONENTS_FOLDER
        for r, d, f in os.walk(components_root_folder):
            for afile in f:
                if afile.endswith('.json'):
                    # print(r, file)
                    with open(os.path.join(r, afile)) as json_file:
                        component = json.load(json_file)
                        # lock_file r+'/'+installed.lock
                        if 'parameters' in component.keys():
                            print('parameters:', component['parameters'])
                        else:
                            print('no parameters:', type(component), component)
