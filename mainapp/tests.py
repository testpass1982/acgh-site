from django.test import TestCase, RequestFactory
from django.test import Client
from django.urls import resolve, reverse
from django.http import HttpRequest
from mainapp.models import Post, Document, DocumentCategory, SidePanel, SiteConfiguration, Component, ColorScheme
from mainapp.models import Service, CenterPhotos, Profstandard, Contact, Profile, Font
# from http import HTTPStatus
from django.shortcuts import get_object_or_404
from mixer.backend.django import mixer
from django.conf import settings
import random
from django.core.files import File
from django.contrib.auth.models import User
from captcha.models import CaptchaStore
import re
import os, sys
from functools import wraps
from time import time
# from mainapp.views import accept_order, index
import mainapp.views as mainapp
from unittest import skip
from django.test.utils import override_settings

# Create your tests here.

# class SmokeTest(TestCase):
#     def test_bad_maths(self):
#         self.assertEqual(1+1, 3)

# PROJECT_NAME = 'acgh-site'


timing_report = {}


def measure_time(func):
    @wraps(func)
    def _time_it(*args, **kwargs):
        start = int(round(time() * 1000))
        try:
            return func(*args, **kwargs)
        finally:
            end_ = int(round(time() * 1000)) - start
            # print(f"Execution time of {func.__name__}: {end_ if end_ > 0 else 0} ms")
            timing_report[func.__name__] = end_ if end_ > 0 else 0
    return _time_it

class SiteTest(TestCase):
    @classmethod
    def setUpClass(cls):
        # print('CWD', os.getcwd())
        cls.project_name = settings.PROJECT_NAME
        email_folder_path = os.path.join(os.getcwd(), 'media', 'email_out')
        if not os.path.exists(email_folder_path):
            os.mkdir(email_folder_path)
        cls.font = Font.objects.create(
            title='Montserrat',
            font_url='<link href="https://fonts.googleapis.com/css?family=Montserrat&display=swap" rel="stylesheet">'
        )
        cls.site_configuration = SiteConfiguration.objects.create(
            title='Конфигурация 1',
            current_color_set="#151A18, #E3C4D2, #D6ABBF, #D2E0FF, #968EAF",
            site_type='1',
            activated=False,
            font=cls.font
            )
        color_scheme = ColorScheme.objects.create(
            title='SEED_B08EA2_analogic-complement',
            colors='#151A18, #E3C4D2, #D6ABBF, #D2E0FF, #968EAF',
            configuration=cls.site_configuration
        )
        cls.site_configuration.activated = True
        cls.site_configuration.save()
        component_data = {
            "relative_scss_path": "scss/components/main-menu-v1/component.scss",
            "title": "main-menu-v1",
            "component_type": "main_menu",
            "html_path": "/home/valentin/{}/mainapp/templates/mainapp/components/main-menu-v1/component.html".format(cls.project_name),
            "relative_js_path": "js/main-menu-v1/",
            "js_path": "",
            "relative_html_path":
            "mainapp/components/main-menu-v1/component.html",
            "code": "main-menu-v1",
            "scss_path": "/home/valentin/{}/assets/scss/components/main-menu-v1/component.scss".format(cls.project_name)
        }
        component_data.update({'configuration': cls.site_configuration})
        slider_component_data = {
            "relative_html_path": "mainapp/components/main-page-slider-v1/component.html",
            "relative_scss_path": "scss/components/main-page-slider-v1/component.scss",
            "relative_js_path": "js/main-page-slider-v1/",
            "scss_path": "/home/valentin/{}/assets/scss/components/main-page-slider-v1/component.scss".format(cls.project_name),
            "html_path": "/home/valentin/{}/mainapp/templates/mainapp/components/main-page-slider-v1/component.html".format(cls.project_name),
            "code": "main-page-slider-v1",
            "js_path": "",
            "component_type": "main_banner",
            "title": "main-page-slider-v1",
            "configuration": cls.site_configuration,
        }
        cls.slider_component = Component.objects.create(**slider_component_data)
        cls.component = Component.objects.create(**component_data)

        cls.post_form_component_data = {
                "html_path": "/home/valentin/{}/mainapp/templates/mainapp/components/main-page-slider-v3/component.html".format(cls.project_name),
                "relative_js_path": "js/main-page-slider-v3/",
                "component_type": "main_banner",
                "title": "main-page-slider-v3",
                "scss_path": "/home/valentin/{}/assets/scss/components/main-page-slider-v3/component.scss".format(cls.project_name),
                "js_path": "",
                "code": "main-page-slider-v3",
                "relative_html_path": "mainapp/components/main-page-slider-v3/component.html",
                "relative_scss_path": "scss/components/main-page-slider-v3/component.scss",
                "configuration": cls.site_configuration
            }
        cls.post_form_component = Component.objects.create(**component_data)

    @classmethod
    def tearDownClass(cls):
        for r, d, f in os.walk(os.path.join(os.getcwd(), 'media')):
            for file in f:
                if file.startswith(('center', 'document', 'file')) and len(file) > 13:
                    os.remove(os.path.join(r, file))
        for r, d, f in os.walk(os.path.join(os.getcwd())):
            for file in f:
                if file in ['component.css', 'component.css.map']:
                    os.remove(os.path.join(r, file))
        print('\n<-TIMING REPORT->')
        for element in sorted((value,key) for (key,value) in timing_report.items()):
            print(element[1], ':', element[0], 'ms')
        # clean media folder


    @measure_time
    def setUp(self):
        self.factory = RequestFactory()

        # self.addCleanup(os.remove, os.path.join(f"{settings.MEDIA_ROOT}", "email_out"))

    @measure_time
    def tearDown(self):
        pass
        # response = self.client.get(reverse('index'))
        # self.assertTrue(response.status_code, 200)


    @measure_time
    def test_main_page_loads_without_errors(self):
        response = self.client.get(reverse('index'))
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<!DOCTYPE html>'))
        self.assertIn('<title>Главная страница</title>', html)
        self.assertTrue(html.strip().endswith('</html>'))
        self.assertTemplateUsed(response, 'mainapp/index.html')

    @measure_time
    def test_can_create_site_configuration_and_add_components(self):
        self.assertTrue(self.component.pk is not None)
        self.assertTrue(self.site_configuration is not None)
        self.assertIn(self.component, Component.objects.filter(
            configuration=self.site_configuration))
        self.assertTrue(self.font.pk == self.site_configuration.font.pk)

    @measure_time
    def test_can_add_font_url_main_page(self):
        response = self.client.get(reverse('index'))
        html = response.content.decode('utf8')
        self.assertIn(self.font.font_url, html)

    @measure_time
    # @skip('too long to execute')
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.filebased.EmailBackend', EMAIL_FILE_PATH = "{mr}/email_out".format(mr=settings.MEDIA_ROOT))
    def test_can_post_form_from_main_page(self):
        for f in os.listdir(os.path.join(settings.MEDIA_ROOT, "email_out")):
            os.remove(os.path.join(settings.MEDIA_ROOT, "email_out", f))

        self.assertTrue(CaptchaStore.objects.count() == 0)
        factory_request = self.factory.get('/')
        factory_response = mainapp.index(factory_request)
        self.assertEqual(CaptchaStore.objects.count(), 2)
        # find captcha hash with re
        f_hash = re.findall(r'value="([0-9a-f]+)"', factory_response.content.decode('utf-8'))[0]
        #get captcha response
        captcha_response = CaptchaStore.objects.get(hashkey=f_hash).response
        request = self.factory.post('/accept_order/', dict(
            # captcha_0=hash_,
            captcha_0=f_hash,
            captcha_1=captcha_response,
            name='tolik_make_tests',
            phone='79257777777'))
        post_response = mainapp.accept_order(request)
        self.assertEqual(post_response.status_code, 200)


    @measure_time
    def test_can_create_and_publish_posts(self):
        titles = ['Post1', 'Post2', 'Часто задаваемые вопросы']
        for i in range(3):
            mixer.blend(Post,
            publish_on_main_page=True,
            publish_in_basement=True,
            title=titles[i])
        response = self.client.get(reverse('index'))

        self.assertTrue(len(response.context['basement_news']), 3)
        post_details_response = self.client.get(
            reverse('details_news', kwargs={'pk': Post.objects.first().pk})
            )
        html = post_details_response.content.decode('utf8')
        self.assertTemplateUsed(post_details_response, 'mainapp/details_news.html')
        self.assertTrue(post_details_response.status_code, 200)
        self.assertIn(Post.objects.first().title, html)
        self.assertIn(Post.objects.first().text, html)

    @measure_time
    def test_can_open_posts_by_details_url(self):
        posts = mixer.cycle(3).blend(Post, publish_on_main_page=True)
        for post in posts:
            url = reverse('details_news', kwargs={'pk': post.pk})
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
            self.assertTrue(isinstance(response.context['post'], Post))
            self.assertEqual(post.title, response.context['post'].title)
            self.assertTrue('related_posts' in response.context)
            self.assertTrue(post not in response.context['related_posts'])

    @measure_time
    def test_can_create_link_holders_and_open_pages(self):
        side_panel = mixer.blend(SidePanel)
        post_center_info = mixer.blend(Post, url_code='CENTER_INFO', title="About us", side_panel=mixer.SELECT)
        response = self.client.get(reverse('index'))
        html = response.content.decode('utf8')
        self.assertTrue('About us' in html)
        details_response = self.client.get(reverse('details', kwargs={'pk': post_center_info.pk}))
        self.assertTrue(details_response.status_code, 200)
        details_html = details_response.content.decode('utf8')
        self.assertTrue(post_center_info.title in details_html)
        self.assertTemplateUsed(details_response, 'mainapp/page_details.html')
        self.assertTrue('side_panel' in details_response.context)
        self.assertTrue(side_panel.text in details_html)

    @measure_time
    def test_can_create_documents_and_publish_them_with_categories(self):
        docs = ['media/document1.doc', 'media/document2.doc', 'media/document3.doc']
        document_categories = mixer.cycle(3).blend(DocumentCategory)
        documents = mixer.cycle(10).blend(
            Document,
            document=File(open(random.choice(docs), 'rb')),
            category=mixer.SELECT
            )
        response = self.client.get(reverse('doc'))
        self.assertTemplateUsed(response, 'mainapp/doc.html')
        self.assertTrue(Document.objects.first() in response.context['docs'])
        self.assertTrue(DocumentCategory.objects.first() in response.context['categories'])
        html = response.content.decode('utf8')
        for doc in Document.objects.all():
            # self.assertTrue(doc.title in html)
            self.assertTrue(doc.category.name in html)
            self.assertTrue(doc.title in html)

    @measure_time
    def test_can_open_all_site_pages(self):
        self.assertTrue(self.client.get(reverse('index')).status_code, 200)
        self.assertTrue(self.client.get(reverse('doc')).status_code, 200)
        mixer.blend(Post)
        self.assertTrue(self.client.get(reverse('details', kwargs={'pk': Post.objects.first().pk})).status_code, 200)
        mixer.blend(Service)
        self.assertTrue(self.client.get(reverse('service_details', kwargs={'pk': Service.objects.first().pk})).status_code, 200)
        self.assertTrue(self.client.get(reverse('cok')).status_code, 200)
        self.assertTrue(self.client.get(reverse('profstandarti')).status_code, 200)
        self.assertTrue(self.client.get(reverse('contacts')).status_code, 200)

    @measure_time
    def test_can_upload_photos_and_publish_them(self):
        component_data = {
            "html_path": "/home/valentin/{}/mainapp/templates/mainapp/components/main-page-content-v1/component.html".format(self.project_name),
            "scss_path": "/home/valentin/{}/assets/scss/components/main-page-content-v1/component.scss", "relative_scss_path": "scss/components/main-page-content-v1/component.scss".format(self.project_name),
            "title": "main-page-content-v1",
            "relative_js_path": "js/main-page-content-v1/",
            "code": "main-page-content-v1",
            "relative_html_path": "mainapp/components/main-page-content-v1/component.html",
            "component_type": "main_page_content",
            "js_path": "",
            "configuration": self.site_configuration
            }
        component = Component.objects.create(**component_data)
        photos = ['media/center_1.jpg', 'media/center_2.jpg', 'media/center_3.jpg']
        for photo in photos:
            mixer.blend(CenterPhotos, image=File(open(photo, 'rb')))

        response = self.client.get(reverse('index'))
        html = response.content.decode('utf8')
        for photo in CenterPhotos.objects.all():
            self.assertTrue(photo.image.url in html)

    @measure_time
    def test_can_make_profstandards_and_publish_them(self):
        profstandards = mixer.cycle(6).blend(Profstandard)
        response = self.client.get(reverse('profstandarti'))
        html = response.content.decode('utf8')
        self.assertTemplateUsed(response, 'mainapp/profstandarti.html')
        self.assertTrue(Profstandard.objects.first() in response.context['profstandards'])
        for ps in profstandards:
            self.assertTrue(ps.title in html)
            self.assertTrue(ps.document.url in html)

    @measure_time
    def test_can_make_contacts_and_publish_them(self):
        contacts = mixer.cycle(5).blend(Contact)
        response = self.client.get(reverse('contacts'))
        self.assertTrue('contacts' in response.context)
        for contact in contacts:
            self.assertTrue(contact.title in response.content.decode('utf8'))
            self.assertTrue(contact.description in response.content.decode('utf8'))
            self.assertTrue(contact.phone in response.content.decode('utf8'))
            self.assertTrue(contact.email in response.content.decode('utf8'))

    @measure_time
    def test_can_load_profile_import_file(self):
        user = mixer.blend(User)
        response = self.client.get('/admin/')
        self.client.force_login(user)
        import_file = File(open('media/import_file_example.txt', 'r'))
        # post a file
        self.client.post('/import_profile/', {'file': import_file})
        # check if posted file updates org profile
        with open('media/import_file_example.txt', 'r') as file:
            for line in file.readlines():
                arr = line.split('::')
                if arr[0] == 'org_short_name':
                    self.assertEqual(arr[1].strip(), Profile.objects.first().org_short_name)
                if arr[0] == 'org_main_phone':
                    self.assertEqual(arr[1].strip(), Profile.objects.first().org_main_phone)
        self.assertTrue(Profile.objects.first() is not None)
        # now logout
        self.client.logout()
        # check if admin panel not present on page
        self.assertNotIn(
            '<div class="admin_panel row bg-light p-3">',
            self.client.get('/').content.decode('utf8')
            )