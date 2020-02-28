"""
File: models.py
Email: yourname@email.com
Description: models to site project
"""
import os
from django.db import models
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import FileExtensionValidator
from ckeditor.fields import RichTextField
from django.utils.text import slugify
from django.urls import reverse
from picklefield.fields import PickledObjectField
from stdimage.models import StdImageField


# Create your models here.
class Tag(models.Model):

    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class Category(models.Model):
    """category model class"""
    name = models.CharField(max_length=64)

    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class ContentMixin(models.Model):
    '''base class for Post, Article and Documents'''
    title = models.CharField(u'Название', max_length=200)
    url_code = models.CharField(u'Код ссылки', max_length=30, blank=True, default='НЕ УКАЗАН')
    short_description = models.CharField(
        u'Краткое описание', max_length=200, blank=True)
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', blank=True)
    published_date = models.DateTimeField(
        u'Дата публикации', blank=True, null=True)
    created_date = models.DateTimeField(u'Дата создания', default=timezone.now)
    text = RichTextUploadingField(
        verbose_name='Текст',
        config_name='default',
        extra_plugins=['youtube'],
        external_plugin_resources=[(
            'youtube',
            'plugins/youtube/',
            # '/static_root/ckeditor/ckeditor/plugins/youtube/',
            # static/ckeditor_plugins/youtube/plugin.js
            'plugin.js',
        )]
    )
    author = models.ForeignKey(
        'auth.User', verbose_name='Автор', on_delete=models.CASCADE)
    publish_on_main_page = models.BooleanField(
        verbose_name="Опубликовать на главной", default=False)

    class Meta:
        abstract = True


class SidePanel(models.Model):
    title = models.CharField(u'Название', max_length=200)
    text = RichTextUploadingField(verbose_name='Текст')

    class Meta:
        verbose_name = 'Боковая панель'
        verbose_name_plural = 'Боковые панели'

    def __str__(self):
        return self.title


class Post(ContentMixin):
    '''child of contentmixin'''
    category = models.ForeignKey(
        Category, verbose_name='Категория', on_delete=models.CASCADE, blank=True)
    publish_on_main_page = models.NullBooleanField(u'Опубликовать на главной', default=False)
    publish_on_news_page = models.BooleanField(
        verbose_name="Опубликовать в ленте новостей", default=False)
    publish_in_basement = models.BooleanField(u'Опубликовать в подвале на главной', default=False)
    side_panel = models.ForeignKey(SidePanel, verbose_name='Боковая панель', blank=True,
                                    null=True, default=None, on_delete=models.SET_NULL)

    class Meta:
        ordering = ['created_date']
        get_latest_by = ['created_date']
        verbose_name = 'Страница'
        verbose_name_plural = "Страницы"

    def get_absolute_url(self):
        return reverse("detailview",
                       kwargs={"content": "post", "pk": self.pk})

    def publish(self):
        """unused function"""
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class PostParameter(models.Model):
    parameter = models.CharField(u'Параметр (json)', max_length=100)
    number = models.SmallIntegerField(u'Порядок вывода')
    post = models.ForeignKey(Post, blank=True, null=True, on_delete=models.CASCADE)


class Article(ContentMixin):
    '''child of ContentMixin'''

    class Meta:
        ordering = ['created_date']
        get_latest_by = ['created_date']
        verbose_name = 'Статья'
        verbose_name_plural = "Статьи"

    def publish(self):
        """unused, left for future"""
        self.published_date = timezone.now()
        self.save()

    def __str__(self):
        return self.title


class DocumentCategory(models.Model):
    name = models.CharField(u'Название категории', max_length=64)
    number = models.SmallIntegerField(verbose_name='Порядок сортировки',
                                    null=True, blank=True, default=None)

    class Meta:
        verbose_name = "Категория документа"
        verbose_name_plural = "Категории документов"

    def __str__(self):
        return self.name

class Document(models.Model):
    """"
    эта модель используется для
    загрузки документов в базу данных
    """
    title = models.CharField(u'Название', max_length=500)
    document = models.FileField(verbose_name='Документ',
                                upload_to="documents/",
                                validators=[FileExtensionValidator(
                                    allowed_extensions=[
                                        'pdf', 'docx', 'doc', 'jpg', 'jpeg'],
                                    message="Неправильный тип файла, используйте\
                                        PDF, DOCX, DOC, JPG, JPEG")])

    category = models.ForeignKey(DocumentCategory, blank=True, null=True, on_delete=models.SET_NULL)
    url_code = models.CharField(u'Код ссылки', max_length=30, blank=True, default='НЕ УКАЗАН')
    uploaded_at = models.DateTimeField(
        verbose_name='Загружен', default=timezone.now)
    tags = models.ManyToManyField(Tag, verbose_name='Тэги', blank=True)
    created_date = models.DateTimeField(
        default=timezone.now, verbose_name='Дата создания')
    post = models.ForeignKey(Post, verbose_name='Страница',
                             blank=True, default='',
                             on_delete=models.SET_NULL,
                             null=True)
    publish_on_main_page = models.BooleanField(
        verbose_name="Опубиковать на главной", default=False)

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"

    def __str__(self):
        return self.title

    def extension(self):
        name, extension = os.path.splitext(self.document.name)
        return extension


def upload_to(instance, filename):
    """left for future, unused function"""
    filename_base, filename_ext = os.path.splitext(filename)
    return "upload/{post_pk}/{filename}{extension}".format(
        post_pk=instance.pk,
        filename=slugify(filename_base),
        extension=filename_ext.lower(),)


def get_image_filename():
    """unused function, left for future"""
    return 'image_{}'.format(slugify(timezone.now()))


class PostPhoto(models.Model):
    """model to load photos to content page"""
    post = models.ForeignKey(Post, verbose_name=u'новость',
                             related_name='images',
                             on_delete=models.SET_NULL,
                             null=True)
    image = models.ImageField(u'изображение', upload_to="upload/")
    title = models.CharField(u'название', max_length=64,
                             blank=True, default=get_image_filename)
    position = models.PositiveIntegerField(u'Позиция', default=0)

    class Meta:
        verbose_name = "Фото"
        verbose_name_plural = "Фотографии"
        ordering = ['position']

    def __str__(self):
        return '{} - {}'.format(self.post, self.image)


class Message(models.Model):
    """this is the class to use within adapter patter realization"""
    STATUS_LIST = (
        (0, 'new'),
        (1, 'registered'),
        (2, 'added_to_sending_queue'),
        (3, 'notify_sent')
    )
    title = models.CharField(u'Заголовок', max_length=64, blank=True)
    typeof = models.CharField(u'Тип сообщения', max_length=64, blank=True)
    params = models.CharField(u'Параметры сообщения',
                              max_length=512, blank=True)
    sender_email = models.EmailField(
        u'Адрес электронной почты', max_length=64, blank=True)
    sender_phone = models.CharField(u'Телефон', max_length=64, blank=True)
    created_date = models.DateTimeField(
        u'Дата получения', default=timezone.now)
    status = models.IntegerField(u'Статус', default=0, choices=STATUS_LIST)

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'

    def __str__(self):
        return self.title

    def set_status(self, status_code):
        # if status_code in STATUS_LIST:
        self.status = status_code


class Contact(models.Model):
    title = models.CharField(u'Название контакта', max_length=64, blank=False)
    description = models.CharField(u'Описание', max_length=200, blank=False)
    email = models.EmailField(
        u'Адрес электронной почты', max_length=64, blank=False)
    phone = models.CharField(u'Телефон', max_length=64, blank=False)
    number = models.SmallIntegerField(u'Порядок вывода на сайт', default=0)

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"

    def __str__(self):
        return self.title


class Staff(models.Model):
    photo = models.ImageField(u'Фотография', upload_to="uploads/", blank=True)
    name = models.CharField(u'ФИО', max_length=120, blank=False)
    job = models.CharField(u'Должность', max_length=120, blank=False)
    experience = models.CharField(u'Опыт работы', max_length=500, blank=True)
    priority = models.SmallIntegerField(u'Приоритет', default=0)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return '{} - {}'.format(self.name, self.job)



class Menu(models.Model):
    """linking main page UI elements with its description"""
    url_code = models.CharField(u'Код ссылки', max_length=30)
    title = models.CharField(u'Заголовок ссылки', max_length=60)
    url = models.CharField(u'Адрес ссылки', max_length=200, default="НЕТ")

    class Meta:
        verbose_name = "Ссылка"
        verbose_name_plural = "Ссылки"

    def __str__(self):
        return self.title


class Registry(models.Model):
    """this is the class to load external registry records"""
    STATUS_LIST = ((0, 'new'), (1, 'published'))
    title = models.CharField(u'Название', max_length=64, blank=True)
    org = models.CharField(u'Организация', max_length=120, blank=True)
    typeof = models.CharField(u'Тип', max_length=64, blank=True)
    params = models.CharField(u'Параметры',
                              max_length=999, blank=True)
    created_date = models.DateField(u'Дата получения', blank=True)
    status = models.IntegerField(u'Статус', default=0, choices=STATUS_LIST)

    class Meta:
        verbose_name = 'Запись реестра'
        verbose_name_plural = 'Записи реестра'

    def __str__(self):
        return self.title

class WeldData(models.Model):
    """database agnostic storage for weld-data"""
    title = models.CharField(u'Название', blank=True, max_length=100)
    uid = models.IntegerField(u'UID', unique=True, blank=True)
    args = PickledObjectField()

    class Meta:
        abstract = True

class Service(models.Model):
    """class for service template"""
    title = models.CharField(
        u'Название услуги', max_length=64, help_text="""
            При добавлении услуги в этот раздел автоматически
            будет создан пункт меню в разделе "Услуги", в котором они
            сортируются в соответствии с порядком сортировки
        """)
    short_description = models.CharField(u'Краткое описание услуги', max_length=200, blank=True, null=True, default=None)
    html = RichTextUploadingField(u'Описание услуги')
    number = models.SmallIntegerField(u'Порядок сортировки', blank=True, null=True, default=None)
    bg_photo = models.ImageField(u'Картинка для главной', upload_to="upload/", null=True, blank=True, default=None)
    documents = models.ManyToManyField(Document, blank=True)
    parent = models.ForeignKey('self', blank=True, null=True, on_delete=models.CASCADE)
    disable_order_button = models.BooleanField(u'Отключить кнопку подачи заявки', default=False)


    class Meta:
        verbose_name = 'Услуга'
        verbose_name_plural = 'Услуги'

    def __str__(self):
        return self.title

class Profile(models.Model):
    """class for templating organization"""
    org_logotype = models.ImageField(u'Логотип организации', upload_to='upload/', blank=True, null=True, default=None)
    org_footer_logotype = models.ImageField(
        u'Логотип для футера (необязательно)',
        upload_to='upload/', blank=True, null=True, default=None)
    org_short_name = models.CharField(u'Краткое название организации', max_length=100, blank=True, null=True, default=None)
    org_full_name = models.CharField(u'Полное название организации', max_length=300, blank=True, null=True, default=None)
    org_intro = models.TextField(u'Текст для главной страницы', blank=True, null=True, default=None)
    org_history = models.TextField(u'История организаици', blank=True, null=True, default=None)
    # phone1 for header
    org_main_phone = models.CharField(u'Главный телефон организации (используется в хедере)', max_length=30, blank=True, null=True, default=None)
    org_main_phone_text = models.CharField(u'Подпись под телефоном в хедере, например "Многоканальный"', max_length=30, blank=True, null=True, default=None)
    # phone2 for header
    org_secondary_phone = models.CharField(u'Второй телефон организации (используется в хедере)', max_length=30, blank=True, null=True, default=None)
    org_secondary_phone_text = models.CharField(u'Подпись под вторым телефоном в хедере, например "Бухгалтерия"', max_length=30, blank=True, null=True, default=None)
    org_phones = models.TextField(u'Телефоны', blank=True, null=True, default=None)
    org_email = models.TextField(u'Адрес электронной почты', blank=True, null=True, default=None)
    org_order_email = models.CharField(u'Адреса для подключения формы заявки', max_length=100, blank=True, null=True, default=None)
    org_header_emails = models.TextField(u'Адреса электронной почты (для хедера)', blank=True, null=True, default=None)
    org_header_phones = models.TextField(u'Телефоны (для хедера)', blank=True, null=True, default=None)
    org_address = models.TextField(u'Адрес местоположения организации', null=True, blank=True, default=None)
    org_address_map_link = models.CharField(u'Ссылка на карту', blank=True, null=True, default=None, max_length=500)
    org_work_time = models.CharField(u'Время работы организации', null=True, blank=True, default=None, max_length=100)
    org_csp_code = models.CharField(u'шифр ЦСП (необязательно)', max_length=20, null=True, blank=True)
    org_csp_reestr_link = models.URLField(u'Ссылка на реестр ЦСП', blank=True, null=True)
    org_acsp_code = models.CharField(u'шифр АЦСП (необязательно)', max_length=20, null=True, blank=True)
    org_acsp_reestr_link = models.URLField(u'Ссылка на реестр АЦСП', blank=True, null=True)
    org_acsm_code = models.CharField(u'шифр АЦСМ (необязательно)', max_length=20, null=True, blank=True)
    org_acsm_reestr_link = models.URLField(u'Ссылка на реестр АЦСМ', blank=True, null=True)
    org_acso_code = models.CharField(u'шифр АЦСО (необязательно)', max_length=20, null=True, blank=True)
    org_acso_reestr_link = models.URLField(u'Ссылка на реестр АЦСО', blank=True, null=True)
    org_acst_code = models.CharField(u'шифр АЦСТ (необязательно)', max_length=20, null=True, blank=True)
    org_acst_reestr_link = models.URLField(u'Ссылка на реестр АЦСТ', blank=True, null=True)
    org_cok_code = models.CharField(u'шифр ЦОК (необязательно)', max_length=20, null=True, blank=True)
    org_cok_reestr_link = models.URLField(u'Ссылка на реестр ЦОК', blank=True, null=True)
    add_ap_list = models.BooleanField(u'Добавить ссылку на список пунктов', default=False)
    add_schedule = models.BooleanField(u'Добавить ссылку на график аттестации', default=False)
    number = models.SmallIntegerField(u'Порядок сортировки', null=True, blank=True)
    class Meta:
        verbose_name = 'Профиль организации'
        verbose_name_plural = 'Профили организации'

    def __str__(self):
        return self.org_short_name

class Profstandard(models.Model):
    title = models.CharField(u'Название профстандарта', max_length=200)
    info = models.CharField(u'Информация о стандарте(код)', max_length=300)
    reg_number = models.CharField(u'Регистрационный номер', max_length=20)
    mintrud_prikaz = models.CharField(u'Приказ минтруда', max_length=100)
    document = models.FileField(u'Файл', upload_to='upload/')
    number = models.SmallIntegerField(u'Порядок сортировки')

    class Meta:
        verbose_name = 'Профстандарт'
        verbose_name_plural = 'Профстандарты'

    def __str__(self):
        return self.title

class Attestat(models.Model):
    title = models.CharField(u'Название аттестата(сертификата)', max_length=60)
    image = models.ImageField(u'Скан аттестата', upload_to="upload/")
    number = models.SmallIntegerField(u'Порядок сортировки')

    class Meta:
        verbose_name = 'Аттестат соответствия'
        verbose_name_plural = 'Аттестаты соответствия'

    def __str__(self):
        return self.title

class Chunk(models.Model):
    """class for making html chunks on pages"""
    title = models.CharField(u'Название вставки', max_length=64)
    code = models.CharField(u'Уникальный код вставки', max_length=64, default='КОД_ВСТАВКИ')
    html = RichTextUploadingField(u'Форматирование вставки')

    class Meta:
        verbose_name = 'Вставка'
        verbose_name_plural = 'Вставки'

    def __str__(self):
        return self.title

class CenterPhotos(models.Model):
    title = models.CharField(u'Название фотографии', max_length=60)
    image = models.ImageField(u'Файл', upload_to="upload/")
    number = models.SmallIntegerField(u'Порядок сортировки', blank=True)

    class Meta:
        verbose_name = 'Фотография центра'
        verbose_name_plural = 'Фотографии центра'

    def __str__(self):
        return self.title

class Font(models.Model):
    title = models.CharField(u'Название шрифта', default=None, blank=True, null=True, max_length=30)
    font_url = models.CharField(u'Ссылка на шрифт', default=None, blank=True, null=True, max_length=200)

    class Meta:
        verbose_name = 'Шрифт'
        verbose_name_plural = 'Шрифты'

    def __str__(self):
        return self.title


class SiteConfiguration(models.Model):

    """class for configuration of site"""
    SITE_TYPES = (
        ('1', 'site_type1'),
        ('2', 'site_type2'),
        ('3', 'site_type3'),
    )
    title = models.CharField(u'Название конфигурации', default='Конфигурация 1', max_length=30)
    site_type = models.CharField(
        u'Тип сайта', max_length=1,
        choices=SITE_TYPES, blank=True, default=None
    )
    color_set_path = models.CharField(
        u'Путь к файлу с переменными SCSS',
        max_length=200, null=True,
        blank=True,
        default='assets/scss/_variables.scss'
    )
    current_color_set = models.CharField(u'Текущие цвета',
        default='#151A18, #E3C4D2, #D6ABBF, #D2E0FF, #968EAF', max_length=50)
    current_component_set = models.CharField(
        u'Текущий набор компонентов',
        max_length=300, blank=True,
        null=True,
        default='main-menu-v1 main-page-slider-v1 main-page-slider-v3 main-page-content-v1')
    font = models.ForeignKey(Font, null=True, blank=True, on_delete=models.SET_NULL)
    activated = models.BooleanField(u'Активировать', default=False)

    class Meta:
        verbose_name = 'Конфигурация сайта'
        verbose_name_plural = 'Конфигурации сайта'

    def __str__(self):
        return self.title

    def update_current_component_set(self):
        if len(Component.objects.all()) > 0:
            self.current_component_set = " ".join([c.title for c in Component.objects.filter(configuration=self.pk)])
            self.save()

class Component(models.Model):
    COMPONENT_TYPE_CHOICES = (
        ('attestats', 'Аттестаты соответствия'),
        ('top_addr_line', 'Верхняя линия с адресом'),
        ('main_menu', 'Главное меню сайта'),
        ('secondary_menu', 'Второстепенное меню'),
        ('main_banner', 'Главный баннер'),
        ('inner_head', 'Хедер для внутренних страниц'),
        ('helper_block', 'Вспомогательный заполнятель пустоты'),
        ('main_page_content', 'Контент главной страницы'),
        ('pict_gallery', 'Галерея фотографий'),
        ('text_block', 'Текстовы блок'),
        ('contact_block', 'Блок с контактами'),
        ('advertising_block', 'Блок с рекламой'),
        ('partners_block', 'Блок с партнерами'),
        ('modal', 'Модальное окно'),
        ('footer', 'Футер')
    )
    title = models.CharField(u'Название компонента', max_length=60)
    code = models.CharField(u'Шифр компонента (латиницей)', max_length=60)

    component_type = models.CharField(
        u'Тип компонента(назначение)',
        max_length=30,
        choices=COMPONENT_TYPE_CHOICES,
        default='не определено'
    )
    html = models.FileField(u'Файл разметки компонента', null=True, blank=True, default=None, upload_to="components/")
    css = models.FileField(u'Файл стилей компонента', null=True, blank=True, default=None, upload_to="components/")
    js = models.FileField(u'Файл скриптов', null=True, blank=True, default=None, upload_to="components/")
    html_path = models.CharField(u'Путь к файлу разметки', blank=True, null=True, max_length=300, default='')
    relative_html_path = models.CharField(u'Относительный путь к файлу разметки', blank=True, null=True, max_length=300, default='')
    scss_path = models.CharField(u'Путь к файлу стилей', blank=True, null=True, max_length=300, default='')
    relative_scss_path = models.CharField(u'Относительный путь к файлу стилей', blank=True, null=True, max_length=300, default='')
    js_path = models.CharField(u'Путь к файлу скрипта', blank=True, null=True, max_length=300, default='')
    relative_js_path = models.CharField(u'Относительный путь к файлу скрипта', blank=True, null=True, max_length=300, default='')
    published = models.BooleanField(u'Опубликовать компонет', default=False)
    main_page = models.BooleanField(u'Компонент главной страницы', default=False)
    number = models.SmallIntegerField(u'Порядок вывода на сайт', default=500)
    configuration = models.ForeignKey(SiteConfiguration, blank=True, null=True, on_delete=models.SET_NULL)


    class Meta:
        verbose_name = 'Компонент сайта'
        verbose_name_plural = 'Компоненты сайта'

    def __str__(self):
        return self.title


class ComponentParameter(models.Model):
    component = models.ForeignKey(Component, on_delete=models.CASCADE)
    parameters = models.CharField(u'Параметры', max_length=500)

    class Meta:
        verbose_name = 'Параметр компонента'
        verbose_name_plural = 'Параметры компонентов'

    def __str__(self):
        return self.parameters

class ColorScheme(models.Model):
    title = models.CharField(u'Название', default='Цветовая схема', max_length=50)
    colors = models.CharField(u'Цвета (через запятую, HEX)', max_length=100)
    configuration = models.ForeignKey(SiteConfiguration, blank=True, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name = 'Цветовая схема'
        verbose_name_plural = 'Цветовые схемы'

    def __str__(self):
        return self.title


class Partner(models.Model):
    title = models.CharField(u'Название партнера', max_length=60)
    logo = models.ImageField(u'Логотип партнера', upload_to="upload/")
    number = models.SmallIntegerField(u'Порядок вывода на сайт')

    class Meta:
        verbose_name = 'Партнер'
        verbose_name_plural = 'Партнеры'

    def __str__(self):
        return self.title

class OrderService(models.Model):
    name = models.CharField(u'Имя контакта', max_length=50)
    phone = models.CharField(u'Телефон контакта', max_length=50)
    compound = models.CharField(u'Состав заявки', max_length=300, default=None, blank=True, null=True)
    ready = models.BooleanField(u'Вопрос решен', default=False, blank=True, null=True)

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'

    def __str__(self):
        return self.name

class SlideBackgrounds(models.Model):
    title = models.CharField(
        u'Название',
        default='Слайдер_{}'.format(timezone.now()),
        max_length=50
    )
    image = StdImageField(
        u'Картинка для фона баннера',
        upload_to='backgrounds/',
        variations={
            'thumbnail': {"width": 200, "height": 100, "crop": True},
            'large': {"width": 1920, "height": 1080, "crop": True}
        }
    )
    activated = models.NullBooleanField(u'Активировать', default=False)

    class Meta:
        verbose_name = 'Картинка для баннера'
        verbose_name_plural = 'Картинки для баннера'

    def __str__(self):
        return self.title