# core import file
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.core.files import File
# from mainapp.models import Menu, Post, Article, PostPhoto, Tag, Category, Chunk, SiteConfiguration, ColorScheme, Font, Component
# from mainapp.models import Contact, Document, Profile, DocumentCategory, Service, CenterPhotos
# from mainapp.models import Attestat
from mainapp.models import *
from django.conf import settings
from mixer.backend.django import mixer
import random
from django.conf import settings
from django.utils import timezone
import os, shutil
from django.contrib.auth.models import User

# from model_mommy.recipe import Recipe, foreign_key, seq
# clean Users
User.objects.all().exclude(username='popov').delete()
# clean upload folder
if os.path.isdir(os.path.join(settings.BASE_DIR, 'media', 'upload')):
    folder = os.path.join(settings.BASE_DIR, 'media', 'upload')
    for a_file in os.listdir(folder):
        a_file_path = os.path.join(folder, a_file)
        try:
            if os.path.isfile(a_file_path):
                os.unlink(a_file_path)
        except Exception as e:
            print('ERROR', e)
# import pdb; pdb.set_trace()

#clean upload/media folder
if os.path.isdir(os.path.join(settings.BASE_DIR, 'media', 'upload', 'media')):
    media_folder = os.path.join(settings.BASE_DIR, 'media', 'upload', 'media')
    for a_file in os.listdir(media_folder):
        # print(a_file)
        a_file_path = os.path.join(media_folder, a_file)
        try:
            if os.path.isfile(a_file_path):
                os.unlink(a_file_path)
        except Exception as e:
            print('ERROR', e)

#clean media/documents/ folder
if os.path.isdir(os.path.join(settings.BASE_DIR, 'media', 'documents', 'media')):
    documents_folder = os.path.join(settings.BASE_DIR, 'media', 'documents', 'media')
    for a_file in os.listdir(documents_folder):
        # print(a_file)
        a_file_path = os.path.join(documents_folder, a_file)
        try:
            if os.path.isfile(a_file_path):
                os.unlink(a_file_path)
        except Exception as e:
            print('ERROR', e)

images = [
    'media/01.JPG',
    'media/02.JPG',
    'media/03.JPG',
    'media/04.JPG',
    'media/05.JPG',
    'media/06.JPG',
]

attestats = [
    'media/sv_1.jpg',
    'media/sv_2.jpg',
    'media/sv_3.jpg',
    'media/sv_4.jpg',
    'media/sv_5.jpg',
]

news_titles = [
    'Конференция НАКС',
    'Общее собрание',
    'Семинар НАКС',
    'Вебинар НАКС',
    'Съезд НАКС',
]

documents = [
    'media/document1.doc',
    'media/document2.doc',
    'media/document3.doc',
    'media/document4.doc'
]

center_photos = [
    'media/center_1.jpg',
    'media/center_2.jpg',
    'media/center_3.jpg',
    'media/center_4.jpg',
    'media/center_5.jpg',
    'media/center_6.jpg',
]

menu_urls = [
    'ABOUT_US', 'ASSP', 'ASSV', 'ATTSP', 'ATTST', 'COK', 'CONTACT', 'DOKZAYAV',
    'INFO', 'OBLD', 'OBLDATT', 'PROFST', 'REGISTRY', 'RKNK', 'SPECSVAR', 'VSENOVOSTI', 'ZAYAV', 'SOSTAV_KOMISS'
]

menu_urls_titles = [
    'О центре', 'Аттестация сварщиков и специалистов', 'Аттестация сварщиков',
    'Аттестация специалистов', 'Аттестация сварочных технологий', 'Центр оценки квалификации',
    'Контакты', 'Документы и заявки', 'Информация для заявителей', 'Область деятельности',
    'Область аттестации', 'Профессиональные стандарты', 'Реестры', 'Разрушающий и неразрушающий контроль',
    'Спецподготовка сварщиков', 'Все новости', 'Заявки', 'Состав комиссии',
]

document_categories = [
    'Аттестация персонала в области сварки',
    'Аттестация сварочных материалов',
    'Аттестация сварочного оборудования',
    'Аттестация сварочных технологий'
]

color_schemes = [
    {
        'title': 'SEED_031927_triad',
        'colors': '#031927, #F099D1, #B0C78D, #9FA3AB, #A5A5B3',
    },
    {
        'title': 'SEED_3E517A_analogic-complement',
        'colors': '#3E517A, #FFE6AA, #F7D690, #B164C4, #DECCD6',
    },
    {
        'title': 'SEED_3E517A_quad',
        'colors': '#3E517A, #9BC0CC, #B89D63, #81FF99, #668AD9',
    },
    {
        'title': 'SEED_3E517A_triad',
        'colors': '#293652, #C77491, #91D674, #82A9FF, #78A3FF',
    },
    {
        'title': 'SEED_693668_analogic-complement',
        'colors': '#3D1F3D, #C7FFCD, #72C274, #B86B5E, #A68E53',
    },
    {
        'title': 'SEED_693668_quad',
        'colors': '#693668, #C79F75, #7CE07F, #364F69, #FCD9F8',
    },
    {
        'title': 'SEED_693668_triad',
        'colors':'#542B53, #CCCC78, #69BBBD, #D66ED4, #FBFF7A',
    },
    {
        'title': 'SEED_85FFC7_analogic-complement',
        'colors': '#030504, #EDE0FF, #F0A3CA, #D2E1FD, #9B8CFE',
    },
    {
        'title': 'SEED_85FFC7_triad',
        'colors': '#274A3A, #B46DF5, #F8C17A, #CBFBE7, #D2FDD6',
    },
    {
        'title': 'SEED_8DAA9D_analogic-complement',
        'colors': '#151A18, #E3C4D2, #D6ABBF, #D2E0FF, #968EAF',
    },
    {
        'title': 'SEED_8DAA9D_quad',
        'colors': '#424F49, #B0AFD1, #E3B8CB, #ABAD8A, #91B6A5',
    },
    {
        'title': 'SEED_8DAA9D_triad',
        'colors': '#3D4A44, #C5B3D6, #D6C5AD, #8AAD9D, #91B6A5',
    },
    {
        'title': 'SEED_B08EA2_analogic-complement',
        'colors': '#6B5663, #60C45E, #ABFFD2, #FFE7CB, #FCFFCB',
    },
    {
        'title': 'SEED_B08EA2_quad',
        'colors': '#755F6C, #9E9B80, #86A894, #8C90B2, #FFC8E8',
    },
    {
        'title': 'SEED_B08EA2_triad',
        'colors': '#5C5C5C, #929E80, #CBE8FF, #FFC9E8, #E8E0FF',
    }
]

fonts = [
    {
        'title': 'Roboto',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Roboto&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Montserrat',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Montserrat&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Literata',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Literata&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Oswald',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Oswald&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Roboto Condensed',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Roboto+Condensed&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Merriweather',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Merriweather&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Noto Sans',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Noto+Sans&display=swap" rel="stylesheet">'
    },
    {
        'title': 'Ubuntu',
        'font_url': '<link href="https://fonts.googleapis.com/css?family=Ubuntu&display=swap" rel="stylesheet">'
    },
]

service_bg_photos = [
    'media/service_sm.jpg',
    'media/service_so.jpg',
    'media/service_sp.jpg',
    'media/service_st.jpg',
]

partners = ['media/alrosa.png', 'media/zabtek.png']

def set_random_component(components, configuration):
    if len(components) > 0:
        components_array = [c for c in components]
        if components.first().component_type in ['top_addr_line', 'helper_block']:
            dice = random.randint(0, 100)
            if dice < 50:
                return
        random_component = random.choice(components_array)
        random_component.configuration = configuration
        random_component.number = random.randint(50, 100) if any([
                    random_component.component_type == 'top_addr_line',
                    random_component.component_type == 'main_menu',
                    random_component.component_type == 'helper_block',
                ]) else 500
        random_component.save()
    else:
        return

class Command(BaseCommand):
    def handle(self, *args, **options):
        #delete all Posts, Articles, Menus and other
        Tag.objects.all().delete()
        Category.objects.all().delete()
        Menu.objects.all().delete()
        Post.objects.all().delete()
        Article.objects.all().delete()
        PostPhoto.objects.all().delete()
        DocumentCategory.objects.all().delete()
        Document.objects.all().delete()
        Contact.objects.all().delete()
        Profile.objects.all().delete()
        Service.objects.all().delete()
        Attestat.objects.all().delete()
        Chunk.objects.all().delete()
        CenterPhotos.objects.all().delete()
        SiteConfiguration.objects.all().delete()
        Font.objects.all().delete()
        Partner.objects.all().delete()
        ColorScheme.objects.all().delete()


        # upload_center_photos
        for i in range(0, len(center_photos)):
            mixer.blend(
                CenterPhotos,
                image=File(open(center_photos[i], 'rb')),
                number=i+1
            )

        # make ColorSchemes
        for i in range(len(color_schemes)):
            ColorScheme.objects.create(
                title=color_schemes[i]['title'],
                colors=color_schemes[i]['colors'])

        # make Chunk for page "About"
        mixer.blend(
            Chunk,
            title='Описание для страницы "о центре"',
            code='about_center',
            html="""
                <p><span style="font-size:18px">Центр аттестации ВВР-2ГАЦ</span></p>
                <p><span style="font-size:18px">Организация является членом Саморегулируемая организация Ассоциация &laquo;НАКС&raquo;.</span></p>
                <p><span style="font-size:18px">Общество с ограниченной ответственностью Аттестационный центр &laquo;НАКС-Владимир&raquo; - является членом СРО Ассоциация&nbsp;&laquo;Национальное Агентство Контроля Сварки&raquo; Системы Аттестации Сварочного производства (САСв) Ростехнадзора и оказывает услуги по аттестации сварщиков и специалистов сварочного производства.</span></p>
                <p><span style="font-size:18px">Директор Герасимова Татьяна Васильевна</span></p>
                <p><span style="font-size:18px">Заместитель директора Лопанов Илья Юрьевич</span></p>
                <p><span style="font-size:18px">Исполнительный директор Сазонов Сергей Феликсович</span></p>
            """
            )

        #make Attestats
        print('Загружаем демо-аттестаты...')
        for i in range(0, len(attestats)):
            mixer.blend(
                Attestat,
                image=File(open(attestats[i], 'rb'))
            )
            print(' Загружен демо-аттестат {}'.format(i+1))

        #make PostPhotos
        print('Загружаем картинки...')

        mixer.cycle(3).blend(
                Article,
                author=User.objects.get(username='popov'),
                publish_on_main_page=True
                )
        for i in range(0, len(images)):
            #make Tags
            mixer.blend(Tag),
            #make Categories
            # mixer.blend(Category),
            #make Posts without pictures
            new_post = mixer.blend(
                Post,
                title=random.choice(news_titles),
                publish_on_main_page=True,
                publish_on_news_page=True,
                published_date=timezone.now(),
                author=User.objects.get(username='popov')
                )
            PostPhoto.objects.create(
                title='{}'.format(images[i]),
                image=File(open(images[i], 'rb')),
                post=new_post
                )
            # mixer.blend(PostPhoto,
            #             image=File(open(images[i], 'rb')))
            #make Articles

            mixer.blend(Contact)
            print('Загружена демо-картинка {}'.format(i+1))
            print('Создана демо-статья {}'.format(i+1))
        for post in Post.objects.all()[3:]:
            post.publish_in_basement=True
            post.save()


        #make Menus
        for i in range(0, len(menu_urls)):
            mixer.blend(Menu, url_code=menu_urls[i], url=reverse(
                'details', kwargs={'pk': Post.objects.first().pk}),
                title=menu_urls_titles[i])

        for i in range(len(document_categories)):
            mixer.blend(DocumentCategory, name=document_categories[i])
            mixer.blend(Service,
            title=document_categories[i],
            html="""
                        <hr>
                        <p>Страница в разработке</p>
                        <hr>
                """,
            bg_photo=File(open(service_bg_photos[i], 'rb')),
            short_description='Краткое описание'
            )

        print('Загружаем демо-документы...')
        for i in range(0, len(documents)):
            mixer.blend(
                Document,
                document=File(open(documents[i], 'rb')),
                category=DocumentCategory.objects.get(
                    pk=random.choice(
                        [category.pk for category in DocumentCategory.objects.all()]
                        ))
            )
            print('Заружен демо-документ {}'.format(i+1))

        print('Создаем демо-профиль...')
        mixer.blend(
            Profile,
            org_full_name='Общество с ограниченной ответственностью "Сварка трубопроводов',
            org_short_name='ООО "Сварка трубопроводов"',
            org_phones='+7 (3842)44-14-90, +7(3842)44-14-92',
            org_email='svarka@naks.ru',
            org_header_email='svarka@naks.ru',
            org_intro="""
                Центр осуществляет аттестационную деятельность в рамках Системы аттестации сварочного производства
                Ростехнадзора (САСв Ростехнадзора), независимую оценку квалификации в области сварки,
                а также оказывает услуги специальной подготовки сварщиков, и специалистов сварочного производства.
                проводит аттестацию сварочного производства (в т.ч. персонала, оборудования, материалов и технологий сварки).
            """,
            org_history="""
                Наша организация аккредитована в области аттестации сварочного производства САСв с января 2000 года. Центр осуществляет
                аттестацию персонала на выполнение сварочных работ (I уровень - сварщик), руководство и технический контроль
                за проведением сварочных работ, включая работы по технической подготовке производства и разработку
                производственно-технологической и нормативной документации (II –IV уровень - специалисты), преподавателей и
                экзаменаторов для всех групп опасных технических устройств. Центр аккредитован для всех видов аттестации
                сварочного оборудования, сварочных материалов и сварочных технологий.
            """,
            org_main_phone="+7(925)601-14-00",
            org_main_phone_text="Многоканальный",
            org_secondary_phone="+7(925)601-14-00",
            org_secondary_phone_text="Бухгалтерия",
            org_header_emails="""svarka@naks.ru, <br>
                                svarka1@naks.ru""",
            org_header_phones='+7 (3842)44-14-90 <br>+7(3842)44-14-92',
            org_address='109469, г. Владимир, улица Полины Осипенко, дом 66',
            org_address_map_link="https://api-maps.yandex.ru/services/constructor/1.0/js/?um=constructor%3A2f2a5847babdf5c0e4cefcc8a84e57a1e46232a8403ac03c80e9e180cba713eb&amp;width=100%25&amp;height=400&amp;lang=ru_RU&amp;scroll=false",
            org_csp_code='ВВР-1ЦСП',
            org_csp_reestr_link="http://naks.ru",
            org_acsp_code='ВВР-2ГАЦ',
            org_acsp_reestr_link="http://naks.ru",
            org_acsm_code='АЦСМ-12',
            org_acsm_reestr_link="http://naks.ru",
            org_acso_code='АЦСО-55',
            org_acso_reestr_link="http://naks.ru",
            org_acst_code='АЦСТ-73',
            org_acst_reestr_link="http://naks.ru",
            org_cok_code='ЦОК-37',
            org_cok_reestr_link='http://naks.ru',
        )
        print('Демо-профиль {} создан'.format(Profile.objects.first().org_short_name))




        # create site_configuration and assign fonts, components and colorschemes
        for f in fonts:
            new_font = mixer.blend(Font, title=f['title'], font_url=f['font_url'])
            print('font created', new_font.title, new_font.pk)
        # mixer.blend(SiteConfiguration)
        configuration = mixer.blend(
            SiteConfiguration,
            title='Конфигурация 1',
            site_type='1',
            font=random.choice([f for f in Font.objects.all()]),
            activated=False
            )
        random_color_scheme = random.choice([c for c in ColorScheme.objects.all()])
        random_color_scheme.configuration = configuration
        random_color_scheme.save()
        configuration.activated = True
        configuration.save()
        top_addr_lines = Component.objects.filter(component_type='top_addr_line')
        inner_heads = Component.objects.filter(component_type='inner_head')
        main_menus = Component.objects.filter(component_type='main_menu')
        main_banners = Component.objects.filter(component_type='main_banner')
        main_page_contents = Component.objects.filter(component_type='main_page_content')
        helper_blocks = Component.objects.filter(component_type='helper_block')
        info_blocks = Component.objects.filter(component_type='advertising_block')
        set_random_component(top_addr_lines, configuration)
        set_random_component(inner_heads, configuration)
        set_random_component(main_menus, configuration)
        set_random_component(main_banners, configuration)
        set_random_component(main_page_contents, configuration)
        set_random_component(helper_blocks, configuration)
        set_random_component(info_blocks, configuration)
        mixer.blend(Post, url_code='CENTER_INFO', title='Информация о центре')
        mixer.blend(Post, url_code='INFO', title='Информация')
        mixer.blend(Post, url_code='OBLD', title='Область деятельности')
        mixer.blend(Post, url_code='SERVICES', title='Услуги')
        mixer.blend(Post, title='Часто задаваемые вопросы')
        mixer.blend(Post, url_code='OK', title='Оценка квалификации в области сварки')
        mixer.blend(Post, url_code='CENTER_MVC', title='Обучение в МВЦ НАКС')
        mixer.blend(Post, url_code='PROFSTANDARTI', title='Профстандарты в сварке')


        for i in range(len(partners)):
            mixer.blend(Partner, logo=File(open(partners[i], 'rb')))
        print('*********fill_db_complete (демо-данные созданы)************')

