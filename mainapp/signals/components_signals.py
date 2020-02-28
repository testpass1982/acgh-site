# from django.core.signals import request_finished
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from mainapp.models import Component, ColorScheme, SiteConfiguration
from django.shortcuts import get_object_or_404
from colour import Color
from django.utils.termcolors import colorize
from django.conf import settings
import shutil, os, subprocess
import json
from django.template import Context, Template
from mainapp.classes import SiteComponent
from django.test import RequestFactory
from mainapp.views import index
# from sass_processor.processor import sass_processor

# {
#     "project_name": "ac_kursk_site",
#     "domain_name": "kursk.minml.ru",
#     "colors": "#151A18, #E3C4D2, #D6ABBF, #D2E0FF, #968EAF"
# }

# @receiver(pre_save, sender=Component)
# def my_callback(sender, **kwargs):
#     print('------------->PRE_SAVE SIGNAL RICIEVED from {}'.format(sender))
def update_sass_variables(color_scheme_pk):
    colorscheme = ColorScheme.objects.get(pk=color_scheme_pk)
    site_colors = [color.strip() for color in colorscheme.colors.split(",")]

    site_colors_pseudo_names = ['$primary', '$secondary', '$neutral',
        '$background', '$highlight']
    color_dict = dict(map(lambda *args: args, site_colors_pseudo_names, site_colors))
    for colr in site_colors:
        colr_obj = Color(colr)
        if colr_obj.luminance >= 0.2:
            darker_luminance = colr_obj.luminance - 0.2
        else:
            darker_luminance = 0
        if colr_obj.luminance <=0.8:
            lighter_luminance = colr_obj.luminance + 0.2
        else:
            lighter_luminance = 1
        darker_color = Color(colr, luminance=darker_luminance)
        color_dict.update(
            {'{}Dark'.format(site_colors_pseudo_names[site_colors.index(colr)]): darker_color.hex_l}
        )
        lighter_color = Color(colr, luminance=lighter_luminance)
        color_dict.update(
            {'{}Light'.format(site_colors_pseudo_names[site_colors.index(colr)]): lighter_color.hex_l}
        )
    with open(colorscheme.configuration.color_set_path, 'w') as color_set_file:
        data = []
        for key, value in color_dict.items():
            data.append("{}: {};\n".format(key, value))
        color_set_file.writelines(data)

def delete_all_css_files():
    assets_path = os.path.join(settings.BASE_DIR, 'assets')
    for r, d, f in os.walk(assets_path):
        for file in f:
            if file in ['style.css', 'style.css.map', 'component.css', 'component.css.map']:
                # print('removing', file)
                os.remove(os.path.join(r, file))
    return True

def copy_and_overwrite(from_path, to_path):
    if os.path.exists(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)

@receiver(post_save, sender=Component)
def update_styles_on_component_save(sender, instance, **kwargs):
    if instance.configuration and instance.title not in instance.configuration.current_component_set:
        try:
            delete_all_css_files()
            request = RequestFactory()
            factory_response = index(request.get('/'))
            collectstatic = subprocess.Popen(["/home/valentin/django2/bin/python3", "manage.py", "collectstatic", "--ignore=*.scss", "--noinput"])
            collectstatic.wait()
        except Exception as e:
            print("COMPONENT EXCEPTION", e)
            # subprocess.Popen(["python3", "manage.py", "collectstatic", "--noinput", "--ignore=*.scss"])
        finally:
            instance.configuration.update_current_component_set()

    try:
        activated_configuration = SiteConfiguration.objects.filter(activated=True).first()
        if not instance.configuration and instance.title in activated_configuration.current_component_set:
            try:
                configuration = SiteConfiguration.objects.filter(activated=True).first()
                configuration.update_current_component_set()
            except Exception as e:
                print('ERROR UPDATING SITE CONFIGURATION', e)
            finally:
                pass
    except Exception as e:
            print('ERROR: NO SITE CONFIGURATION')
            pass

@receiver(post_save, sender=ColorScheme)
def update_configuration_colors(sender, instance, **kwargs):
    # /home/valentin/acgh-site/assets/scss/components/helper-block-v1/component.scss
    # /home/valentin/acgh-site/static/scss/component.scss
    if instance.configuration:
        other_schemes = ColorScheme.objects.all().exclude(pk=instance.pk)
        for scheme in other_schemes:
            if scheme.configuration:
                scheme.configuration = None
                scheme.save()
        configuration = instance.configuration
        configuration.save()
            # import pdb; pdb.set_trace()
        if instance.colors != configuration.current_color_set:
            try:
                update_sass_variables(instance.pk)
                delete_all_css_files()
                request = RequestFactory()
                factory_response = index(request.get('/'))
                collectstatic = subprocess.Popen(["/home/valentin/django2/bin/python3", "manage.py", "collectstatic", "--ignore=*.scss", "--noinput"])
                collectstatic.wait()
            except Exception as e:
                print('COLORSCHEME EXCEPTION', e)
                # subprocess.Popen(["python3", "manage.py", "collectstatic", "--noinput", "--ignore=*.scss"])
            finally:
                configuration.current_color_set = instance.colors
                configuration.save()

        # if settings.DEBUG is False:
        # assets_scss_path = os.path.join(settings.BASE_DIR, 'assets', 'scss')
        # static_root_scss_path = os.path.join(settings.BASE_DIR, 'static_root', 'scss')
        # copy_and_overwrite(assets_scss_path, static_root_scss_path)
        # for r, d, f in os.walk(assets_path):
        #     for file in f:
        #         if file in ['component.css', 'component.css.map', 'style.css', 'style.css.map']:
        #             # /home/valentin/acgh-site/static_root/scss/components/info-block-v1/component.css
        #             src_path = os.path.join(r, file)
        #             dst_path = src_path.replace('assets', 'static_root')
        #             if os.path.isfile(dst_path):
        #                 os.remove(dst_path)
        #                 shutil.copy(src_path, dst_path)
        #             if not os.path.isfile(dst_path):
        #                 shutil.copy(src_path, dst_path)

        # src_file = os.path.join(settings.BASE_DIR, 'assets', 'scss', '_variables.scss')
        # dst_file = os.path.join(settings.BASE_DIR, 'static_root', 'scss', '_variables.scss')
        # if os.path.isfile(dst_file):
        #     os.remove(dst_file)
        # print('POST_SAVE SIGNAL -> CONFIGURATION {} UPDATED'.format(configuration))

# @receiver(pre_save, sender=SiteConfiguration)
@receiver(pre_save, sender=SiteConfiguration)
def callback(sender, instance, **kwargs):
    if instance.activated:
        print('configuration instance activated')
    # print(colorize('COLORSCHEME VARIABLES UPDATED', bg='blue'))

