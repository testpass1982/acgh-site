from django.contrib import admin
from django.urls import reverse
from django.utils.encoding import force_text
from django.utils.html import format_html

from .models import *
# from .models import WeldData
# from .domain_model import WeldOrg, Welder
# Register your models here.




def get_picture_preview(obj):
    if obj.pk:  # if object has already been saved and has a primary key, show picture preview
        return format_html("""<a href="{src}" target="_blank">
        <img src="{src}" alt="{title}" style="max-width: 200px; max-height: 200px;" />
        </a>""".format(
            src=obj.image.url,
            title=obj.title,
        ))
    return "(После загрузки фотографии здесь будет ее миниатюра)"


get_picture_preview.allow_tags = True
get_picture_preview.short_description = "Предварительный просмотр:"


def get_colors_preview(obj):
    if obj.pk:
        scheme = obj.colors.split(',')
        scheme_render_arr = []
        for color in scheme:
            # scheme_render_arr.append('<button class="jscolor" style="width: 50px; height: 50px; background-color: {};"></button>'.format(color))
            scheme_render_arr.append("""
            <input class="jscolor rect" value="{color}" class="rect" style="width: 50px; height: 50px;"></input>
            """.format(color=color))
        # import pdb; pdb.set_trace()
        return format_html("""
            <div style="display: flex; flex-flow: row nowrap; justify-content: space-between;">
                {}
            </div>
        """.format("".join(scheme_render_arr)))

get_colors_preview.allow_tags = True
get_colors_preview.short_description = "Предварительный просмотр цветов:"


def get_url(obj):
    # Надо обязательно изменить на боевом сервере адрес ссылки
    if obj.pk:
        return format_html(
            '<a href="{}" target="_blank">http://127.0.0.0{}</a>'.format(
                obj.get_absolute_url(), obj.get_absolute_url()))


get_url.allow_tags = True
get_url.short_description = "Ссылка на страницу"


class PostPhotoInline(admin.StackedInline):
    model = PostPhoto
    extra = 0
    fields = [
        'id', "get_edit_link", "title", "image", "position",
        get_picture_preview
    ]
    readonly_fields = ['id', "get_edit_link", get_picture_preview]

    def get_edit_link(self, obj=None):
        if obj.pk:  # if object has already been saved and has a primary key, show link to it
            url = reverse(
                'admin:%s_%s_change' % (obj._meta.app_label,
                                        obj._meta.model_name),
                args=[force_text(obj.pk)])
            return format_html("""<a href="{url}">{text}</a>""".format(
                url=url,
                text="Редактировать %s отдельно" % obj._meta.verbose_name,
            ))
        return "(Загрузите фотографию и нажмите \"Сохранить и продолжить редактирование\")"

    get_edit_link.short_description = "Изменить"
    get_edit_link.allow_tags = True


class DocumentInline(admin.StackedInline):
    model = Document
    extra = 0
    fields = ['id', "title", 'document']
    list_display = ['title', 'publish_on_main_page']


def get_tag_list(obj):
    return [tag.name for tag in obj.tags.all()]


get_tag_list.allowtags = True
get_tag_list.short_description = 'Список тэгов'


from .models import Component


class ComponentInline(admin.StackedInline):
    model = Component
    extra = 0
    verbose_name = 'компонент'
    verbose_name_plural = 'Создать связанный компонент'
    # fields = ['title', 'code', 'number']
    readonly_fields = ['id', get_colors_preview]
    # list_display = ['title']

from django import forms


# class ComponentModelForm(forms.ModelForm):
#     CHOICES = [(comp.id, comp.code) for comp in Component.objects.all().order_by('number')]
#     class Meta:
#         model = Component
#         exclude = (
#             # 'code',
#             # 'component_type',
#             'html',
#             'css',
#             'js',
#             'html_path',
#             'relative_html_path',
#             'scss_path',
#             'relative_scss_path',
#             'js_path',
#             'relative_js_path',
#         )

#     pk = forms.ChoiceField(choices=CHOICES)

class ChooseExistingComponentInline(admin.TabularInline):
    model = Component
    # form = ComponentModelForm
    extra = 0
    verbose_name = 'компонент'
    verbose_name_plural = 'Выбрать существующие компоненты'

class ColorSchemeInline(admin.StackedInline):
    model = ColorScheme
    extra = 0
    verbose_name = 'цветовая схема'
    verbose_name_plural = 'цветовые схемы'
    readonly_fields = ['id', get_colors_preview]

@admin.register(SiteConfiguration)
class SiteConfigurationAdmin(admin.ModelAdmin):
    inlines = [ComponentInline, ColorSchemeInline]
    # import pdb; pdb.set_trace()
    list_display = ['title', 'site_type', 'activated']

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'url_code', get_tag_list, 'publish_on_main_page']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'publish_on_main_page', 'created_date']


def show_url(obj):
    return '<a href="{}">View on site</a>'.format(obj.get_absolute_url())


show_url.allow_tags = True


class PostParameterInline(admin.StackedInline):
    model = PostParameter
    extra = 0


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # save_on_top = True
    view_on_site = True

    fields = [
        'id', 'title', 'url_code', 'side_panel', 'tags', 'category', 'author', 'short_description',
        'text', get_url, 'created_date', 'published_date',
        'publish_on_main_page', 'publish_on_news_page', 'publish_in_basement',
    ]
    readonly_fields = ['id', get_url]
    list_display = [
        'title', 'category', 'created_date', 'publish_on_main_page',
        'publish_on_news_page', 'url_code',
    ]
    inlines = [PostPhotoInline, DocumentInline, PostParameterInline]

    def view_on_site(self, obj):
        url = reverse('detailview', kwargs={'content': 'post', 'pk': obj.pk})
        return  url


@admin.register(PostPhoto)
class PostPhotoAdmin(admin.ModelAdmin):
    # save_on_top = True
    fields = ['id', "post", "image", "title", "position", get_picture_preview]
    readonly_fields = ['id', get_picture_preview]
    list_display = ['title', 'post', get_picture_preview]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['title', 'typeof', 'params', 'sender_email', 'status']

@admin.register(CenterPhotos)
class CenterPhotoAdmin(admin.ModelAdmin):
    list_display = ['title', 'number']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['title', 'number']

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['title', 'number', 'parent']

from django.db import models
from django.forms import TextInput


class ComponentParameterInline(admin.StackedInline):
    model = ComponentParameter
    extra = 0
    fields = [
        'id', "parameters",
    ]
    # def formfield_for_dbfield(self, db_field, **kwargs):
    # # This method will turn all TextFields into giant TextFields
    #     if isinstance(db_field, models.TextField):
    #         return forms.CharField(widget=forms.Textarea(attrs={'cols': 130, 'rows':30}))
    #     return super(ComponentParameterInline, self).formfield_for_dbfield(db_field, **kwargs)

@admin.register(Component)
class ComponentAdmin(admin.ModelAdmin):
    list_display = ['title', 'id', 'number', 'configuration']
    formfield_overrides = {
        models.CharField: {'widget': TextInput(attrs={'size':'100'})},
        # models.TextField: {'widget': Textarea(attrs={'rows':4, 'cols':40})},
    }

    inlines = [ComponentParameterInline]

@admin.register(ColorScheme)
class ColorSchemeAdmin(admin.ModelAdmin):
    list_display = ['title', get_colors_preview, 'id', 'configuration']
    readonly_fields = ['id', get_colors_preview]

    class Media:
        js = ('js/jquery-3.3.1.min.js', 'js/admin_colors.js', 'js/jscolor.js')


@admin.register(OrderService)
class OrderServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'ready', 'compound']
    fields = ['name', 'phone', 'compound', 'ready']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['name', 'job', 'priority']

admin.site.register(Partner)
admin.site.register(SlideBackgrounds)
admin.site.register(Font)
admin.site.register(Tag)
admin.site.register(Category)
# admin.site.register(Staff)
admin.site.register(Registry)
admin.site.register(SidePanel)
admin.site.register(Attestat)
admin.site.register(Profile)
admin.site.register(Profstandard)
admin.site.register(DocumentCategory)