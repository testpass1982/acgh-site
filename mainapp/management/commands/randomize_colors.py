from django.core.management.base import BaseCommand
from mainapp.models import SiteConfiguration, Font, Component, ColorScheme
from django.conf import settings
import requests
import json
import random
import colour
# import os

# with open(os.path.join(settings.BASE_DIR, 'secret.json'), 'r') as secret_file:
#     secret = json.load(secret_file)
#     ADMIN, PASSWORD, EMAIL = secret['site_admin'], secret['site_admin_password'], secret['site_admin_email']
# COLOR_MODES = ['triad', 'analogic-complement', 'analogic', 'quad', 'monochrome-dark']
# COLOR_MODES = ['triad', 'quad', 'analogic-complement']
COLOR_MODES = ['triad', 'quad', 'analogic-complement']
SEED_COLORS = ['3E517A', 'B08EA2', '031927', '693668', '8DAA9D']

class Command(BaseCommand):
    def handle(self, *args, **options):
        ColorScheme.objects.all().delete()
        # Choices: monochrome monochrome-dark monochrome-light analogic complement analogic-complement triad quad
        # address = 'http://www.thecolorapi.com/scheme?hex=0047AB&mode=triad&count=6&format=json'
        for algorythm in COLOR_MODES:
            for seed_color in SEED_COLORS:
                print('****NEW SCHEME****')
                address = 'http://thecolorapi.com/scheme?hex={}&format=json&mode={}&count=4'.format(seed_color, algorythm)
                r = requests.get(address)
                json_request = r.json()
                colors_array = ['#{}'.format(seed_color)]
                for color in json_request['colors']:
                    print('COLOR', color['hex']['value'])
                    colors_array.append(color['hex']['value'])

                ColorScheme.objects.create(title='SEED_{}_{}'.format(seed_color, algorythm), colors=', '.join(colors_array))
                print('NEW COLORSCHEME CREATED')

        #make primary color of all color schemes darker
        #random set of configuration
        all_colorschemes = ColorScheme.objects.all()
        for color_scheme in all_colorschemes:
            colors_arr = [color.strip() for color in color_scheme.colors.split(',')]
            #check primary must be darker
            #check secondary must be lighter
            # import pdb; pdb.set_trace()
            first_color = colour.Color(colors_arr[0])
            second_color = colour.Color(colors_arr[1])
            if first_color.luminance > 0.7 and second_color.luminance < 0.3:
                print('------------------>luminance updating<---------------------')
                first_color.luminance = 0.3
                second_color.luminance = 0.7
                colors_arr[0], colors_arr[1] = first_color.hex_l, second_color.hex_l
                color_scheme.colors = ", ".join(colors_arr)
            color_scheme.configuration = None
            color_scheme.save()
        random_color_scheme = random.choice([color for color in all_colorschemes])
        configuration = SiteConfiguration.objects.first()
        random_color_scheme.configuration = configuration
        random_color_scheme.save()
        configuration.save()
