import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponseRedirect
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import PostForm, ArticleForm, DocumentForm, ProfileImportForm, OrderForm
from .forms import SendMessageForm, SubscribeForm, AskQuestionForm, SearchRegistryForm
from .adapters import MessageModelAdapter
from .message_tracker import MessageTracker
from .utilites import UrlMaker, update_from_dict
from .registry_import import Importer, data_url
from django.conf import settings
from django.template.loader import render_to_string
from .classes import SiteComponent
from django.core.mail import send_mail
from django.urls import resolve
from .models import *

# Create your views here.

def accept_order(request):
    if request.method == 'POST':
        # print('REQUEST POST', request.POST)
        data = {
            "name": request.POST.get('name'),
            "phone": request.POST.get('phone'),
            "captcha_1": request.POST.get('captcha_1'),
            "captcha_0": request.POST.get('captcha_0'),
            }
        order_variants = ['attst', 'attso', 'attsvsp', 'attlab', 'attsm']
        if any([request.POST.get(order_item) for order_item in order_variants]):
            order_compound = {
                "Аттестация технологий": 'attst' in request.POST,
                "Аттестация оборудования": 'attso' in request.POST,
                "Аттестация персонала": 'attso' in request.POST,
                "Аттестация лаборатории": 'attlab' in request.POST,
                "Аттестация материалов": 'attsm' in request.POST,
            }
            data.update({"compound": "{}".format(order_compound)})
        else:
            order_compound = {'Ничего не заявлено': True}
        form = OrderForm(data)
        if form.is_valid():
            instance = form.save()
            current_absolute_url = request.build_absolute_uri()
            email_address_arr = ['valentin.anatoly@gmail.com']
            order_arr = []

            for key in order_compound.keys():
                if order_compound[key] is True:
                    order_arr.append(key)

            if '8000' not in current_absolute_url:
                if Profile.objects.first() is not None:
                    admin_email_address = Profile.objects.first().org_order_email.split(" ")
                else:
                    admin_email_address = 'valentin@naks.ru'
                email_address_arr += admin_email_address
            # 4seconds economy to send_email every time i make tests
            if not instance.name == 'tolik_make_tests':
                send_mail(
                    'Заполнена заявка на сайте',
    """
    Заполнена заявка на сайте {url}
    Имя: {name}, Телефон: {phone},
    Заявлено: {order_string}
    """.format(url=current_absolute_url, name=instance.name, phone=instance.phone, order_string=", ".join(order_arr)),
                    settings.EMAIL_HOST_USER,
                    email_address_arr
                )
            return JsonResponse({'message': 'ok', 'order_id': instance.pk})
        else:
            return JsonResponse({'errors': form.errors})


def index(request):
    title = 'Главная страница'
    """this is mainpage view with forms handler and adapter to messages"""
    # tracker = MessageTracker()
    if request.method == 'POST':
        request_to_dict = dict(zip(request.POST.keys(), request.POST.values()))
        form_select = {
            'send_message_button': SendMessageForm,
            'subscribe_button': SubscribeForm,
            'ask_question': AskQuestionForm,
        }
        for key in form_select.keys():
            if key in request_to_dict:
                print('got you!', key)
                form_class = form_select[key]
        form = form_class(request_to_dict)
        if form.is_valid():

            # saving form data to messages (need to be cleaned in future)
            adapted_data = MessageModelAdapter(request_to_dict)
            adapted_data.save_to_message()
            print('adapted data saved to database')
            tracker.check_messages()
            tracker.notify_observers()
        else:
            raise ValidationError('form not valid')

    pictured_posts = {}
    main_page_posts = Post.objects.filter(publish_on_main_page=True).order_by('published_date')[:3]
    for post in main_page_posts:
        pictured_posts[post] = PostPhoto.objects.filter(post__pk=post.pk).first()

    content = {
        'title': title,
        'center_photos': CenterPhotos.objects.all().order_by('number'),
        'partners': Partner.objects.all().order_by('number'),
        'component_name': 'VASYA',
        'pictured_posts': pictured_posts,
        'not_pictured_posts': Post.objects.filter(publish_in_basement=True),
        'documents': Document.objects.filter(publish_on_main_page=True).order_by('-created_date'),
        'articles': Article.objects.filter(publish_on_main_page=True).order_by('-created_date'),
        'slide_background': SlideBackgrounds.objects.filter(activated=True).first(),
    }
    # main-page-slider-v1
    configuration = SiteConfiguration.objects.first()
    activated_components = Component.objects.filter(configuration=configuration)
    faq_component = Component.objects.get(title='main-page-slider-v1')
    if faq_component in activated_components:
        try:
            content.update({'faq': Post.objects.get(title='Часто задаваемые вопросы')})
        except:
            content.update({'faq': {'title': 'Добавьте страницу faq в админке',
                                    'text': '<p class="text text-danger">Страница faq не создана</p>'}
                            })
    # import pdb; pdb.set_trace()
    return render(request, 'mainapp/index.html', content)

def reestr(request):
    title = 'Реестр'

    content = {
        'title': title
    }
    return render(request, 'mainapp/reestr.html', content)


def doc(request):
    from .models import DocumentCategory

    content={
        "title": "Документы",
        'docs': Document.objects.all(),
        'categories': DocumentCategory.objects.all()
    }
    return render(request, 'mainapp/doc.html', content)

def partners(request):
    return render(request, 'mainapp/partners.html')

def page_details(request, pk=None):

    post = get_object_or_404(Post, pk=pk)
    parameters = PostParameter.objects.filter(post=post).order_by('number')
    images = PostPhoto.objects.filter(post__pk=pk)
    page_parameters = []
    for param in parameters:
        json_parameter = json.loads(param.parameter)
        if json_parameter['include_component']:
            included_component_name = json_parameter['include_component']
            component = Component.objects.filter(title=included_component_name).first()
            page_parameters.append(SiteComponent(component))

    side_panel = post.side_panel
    # service = get_object_or_404(Service, pk=pk)
    content = {
        'title': 'Детальный просмотр',
        'post': post,
        'side_panel': side_panel,
        'images': images,
        'page_parameters': page_parameters
    }
    return render(request, 'mainapp/page_details.html', content)

def article_details(request, pk=None):
    post = get_object_or_404(Article, pk=pk)
    content = {
        'title': 'Детальный просмотр',
        'post': post,
    }
    return render(request, 'mainapp/page_details.html', content)

def service_details(request, pk=None):
    service = get_object_or_404(Service, pk=pk)
    content = {
        'title': 'Детальный просмотр',
        'post': service,
    }
    return render(request, 'mainapp/page_details.html', content)

def cok(request):
    spks_documents = Document.objects.filter(
        tags__in=Tag.objects.filter(name="НПА СПКС")
    ).order_by('-created_date')
    spks_example_documents = Document.objects.filter(
        tags__in=Tag.objects.filter(name="Образцы документов СПКС")
    )
    content = {
        'title': 'cok_documets',
        'spks_documents': spks_documents,
        'spks_example_documents': spks_example_documents
    }
    return render(request, 'mainapp/cok.html', content)

def profstandarti(request):
    from .models import Profstandard
    profstandards = Profstandard.objects.all().order_by('number')
    content = {
        'title': 'Профессиональные стандарты',
        'profstandards': profstandards,
    }
    return render(request, 'mainapp/profstandarti.html', content)
def contacts(request):

    content = {
        'title': 'Контакты',
        'contacts': Contact.objects.all().order_by('number')
    }
    if Post.objects.filter(url_code='WALKTHROUGH').count() > 0:
        walkthrough = Post.objects.get(url_code="WALKTHROUGH")
        content.update({
            'walktrough': walkthrough
        })
        # import pdb; pdb.set_trace()
    return render(request, 'mainapp/contacts.html', content)
def all_news(request):
    content = {
        'title': 'All news',
        'news': Post.objects.all().order_by('-published_date')[:9]
    }
    return render(request, 'mainapp/all_news.html', content)

def political(request):
    political_documents = Document.objects.filter(
        tags__in=Tag.objects.filter(name="НПА СПКС")
    ).order_by('-created_date')
    political_example_documents = Document.objects.filter(
        tags__in=Tag.objects.filter(name="Образцы документов СПКС")
    )
    content = {
        'title': 'political_documets',
        'political_documents': political_documents,
        'political_example_documents': political_example_documents
    }
    return render(request, 'mainapp/political.html', content)

def details_news(request, pk=None):

    return_link = HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    post = get_object_or_404(Post, pk=pk)
    related_posts = Post.objects.filter(publish_on_news_page=True).exclude(pk=pk)[:3]
    attached_images = PostPhoto.objects.filter(post__pk=pk)
    attached_documents = Document.objects.filter(post__pk=pk)
    post_content = {
        'post': post,
        'related_posts': related_posts,
        'images': attached_images,
        'documents': attached_documents,
    }

    return render(request, 'mainapp/details_news.html', post_content)

def import_profile(request):
    content = {}
    if request.method == "POST":
        if len(request.FILES) > 0:
            form = ProfileImportForm(request.POST, request.FILES)
            if form.is_valid():
                data = request.FILES.get('file')
                file = data.readlines()
                import_data = {}
                for line in file:
                    string = line.decode('utf-8')
                    if string.startswith('#') or string.startswith('\n'):
                        # print('Пропускаем: ', string)
                        continue
                    splitted = string.split("::")
                    import_data.update({splitted[0].strip(): splitted[1].strip()})
                    # print('Импортируем:', string)
                profile = Profile.objects.first()
                if profile is None:
                    profile = Profile.objects.create(org_short_name="DEMO")
                try:
                    #updating existing record with imported fields
                    update_from_dict(profile, import_data)
                    content.update({'profile_dict': '{}'.format(profile.__dict__)})
                    content.update({'profile': profile})
                    # print('***imported***')
                except Exception as e:
                    print("***ERRORS***", e)
                    content.update({'errors': e})
        else:
            content.update({'errors': 'Файл для загрузки не выбран'})
        return render(request, 'mainapp/includes/profile_load.html', content)

def test_component(request, pk):
    c = get_object_or_404(Component, pk=pk)
    component_context = { 'name': 'VASYA', 'given_context': 'context_of_component' }
    page_component = SiteComponent(c, component_context)
    # can include component - give it a content
    # can component.render - give a context directly to component
    content = {
        'component': page_component
    }

    return render(request, 'mainapp/component_template.html', content)

def inner(request):
    return render(request, 'mainapp/inner.html')

def acgh_contacts(request):
    return render(request, 'mainapp/acgh-contacts.html')