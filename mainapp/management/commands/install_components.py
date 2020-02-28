from django.core.management.base import BaseCommand
from mainapp.models import Component
from django.core.files import File
from django.conf import settings
import json
import os
import shutil
import time
from django.utils.termcolors import colorize


COMPONENTS_FOLDER = os.path.join(settings.BASE_DIR, 'mainapp', 'templates', 'mainapp', 'components')
SCSS_FOLDER = os.path.join(settings.BASE_DIR, 'assets', 'scss', 'components')
JS_FOLDER = os.path.join(settings.BASE_DIR, 'static', 'js')
IMAGES_FOLDER = os.path.join(settings.BASE_DIR, 'static', 'img')
SCSS_RELATIVE_FOLDER = 'scss/components'
JS_RELATIVE_FOLDER = 'js'
TEMPLATE_RELATIVE_FOLDER = 'mainapp/components'
IMAGES_RELATIVE_FOLDER = 'img'

class Command(BaseCommand):
    def __init__(self):
        super().__init__()
        self.template_folder_name = ''
        self.json_file = ''
        self.html_file = ''
        self.scss_file = ''
        self.js_file = ''
        self.component_title = ''
        #self.parameters

    def add_arguments(self, parser):
        parser.add_argument('-u', '--undo', action='store_true', help="use it for uninstall all components")

    def handle(self, *args, **options):
        if options['undo']:
            print('UNINSTALLING')
            time.sleep(2)
            return
        else:
            components_root_folder = COMPONENTS_FOLDER
            for component_folder in os.listdir(components_root_folder):
                self.component_title = component_folder
                # if component_folder.startswith(COMPONENT_FOLDER_NAME_PATTERN):
                # print('FOUND COMPONENT FOLDER', component_folder)
                self.template_folder_name = component_folder
                if 'installed.lock' in os.listdir(os.path.join(
                        components_root_folder, component_folder)):
                    lock_file = os.path.join(components_root_folder, component_folder, 'installed.lock')
                    self.check_installed_lock(lock_file)
                    continue
                else:
                    folder_list = os.listdir(os.path.join(components_root_folder, component_folder))
                    folder_path = os.path.join(components_root_folder, component_folder)
                    for afile in folder_list:
                        if afile.endswith('html'):
                            #this file will always place here, it will not be moved to another folder
                            self.html_file = os.path.join(folder_path, afile)
                        if afile.endswith('scss'):
                            self.move_file_to_folder(
                                #from:
                                os.path.join(folder_path, afile),
                                #to:
                                os.path.join(SCSS_FOLDER, self.component_title)
                                )
                            self.scss_file = os.path.join(SCSS_FOLDER, self.component_title, afile)
                        if afile.endswith('js'):
                            js_file = os.path.join(folder_path, afile)
                            self.move_file_to_folder(
                                os.path.join(folder_path, afile),
                                os.path.join(JS_FOLDER, self.component_title)
                                )
                            self.js_file = os.path.join(JS_FOLDER, self.component_title, afile)
                        if afile.endswith('json'):
                            json_file = os.path.join(folder_path, afile)
                            with open(json_file, 'r') as json_file:
                                self.parameters = json.load(json_file)
                        if afile.startswith('img'):
                            for f in os.listdir(os.path.join(folder_path, afile)):
                                try:
                                    print('FILE:', f)
                                    image_file_path = os.path.join(folder_path, afile, f)
                                    self.move_file_to_folder(image_file_path, IMAGES_FOLDER)
                                except Exception as e:
                                    print('SOMETHING GO WRONG ', e)
                            #remove img folder
                            os.rmdir(os.path.join(components_root_folder, component_folder, 'img'))
                self.update_parameters()
                self.create_component_object(self.parameters)
                self.create_lock_file()

    def move_file_to_folder(self, afile, folder):
        try:
            print('moving a file {}'.format(afile))
            #rename a file adding a component name
            # old_name = os.path.basename(afile)
            # new_name = self.component_title+'__'+old_name
            if not os.path.exists(folder):
                os.mkdir(folder)
            shutil.move(afile, folder)
            # import pdb; pdb.set_trace()
            print('-------->file moved to {}'.format(folder))
        except Exception as e:
            print(e, 'ERROR MOVING A PICT FILE')

    def update_parameters(self):
        html_file_name = os.path.basename(self.html_file)
        scss_file_name = os.path.basename(self.scss_file)
        js_file_name = os.path.basename(self.js_file)
        self.parameters.update({
            'title': self.component_title,
            'code': self.template_folder_name,
            'html_path': self.html_file,
            'scss_path': self.scss_file,
            'js_path': self.js_file,
            'relative_html_path': '{}/{}/{}'.format(
                TEMPLATE_RELATIVE_FOLDER, self.component_title, html_file_name),
            'relative_scss_path': '{}/{}/{}'.format(
                SCSS_RELATIVE_FOLDER, self.component_title, scss_file_name),
            'relative_js_path': '{}/{}/{}'.format(
                JS_RELATIVE_FOLDER, self.component_title, js_file_name)
        })
        print('***parameters updated: ', self.parameters)

    def create_component_object(self, options):
        component = Component.objects.create(**options)
        print(colorize('*** COMPONENT CREATED: {}, pk: {}'.format(
            component.title, component.pk), bg='yellow', fg='blue'))

    def add_link_to_base_html(self, afile):
        pass

    def create_lock_file(self):
        with open(os.path.join(COMPONENTS_FOLDER, self.template_folder_name, 'installed.lock'), 'w') as f:
            data = self.parameters
            f.write(str(json.dumps(data)))
            print('done creating lock file')

    def check_installed_lock(self, file):
        print('FILE', file)
        with open(file, 'r') as f:
            lock_data = f.read()
            lock_json = json.loads(lock_data)
            # import pdb; pdb.set_trace()
            print('LOCK_JSON', lock_json['title'])
            try:
                component = Component.objects.get(title=lock_json['title'])
                print('COMPONENT {} in database'.format(component.title))
            except Component.DoesNotExist:
                self.create_component_object(lock_json)


