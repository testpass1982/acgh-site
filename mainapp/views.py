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
        # import pdb; pdb.set_trace()
        form = OrderForm(request.POST)
        if form.is_valid():
            instance = form.save()
            current_absolute_url = request.build_absolute_uri()
            email_address_arr = ['popov.anatoly@gmail.com']
            order_arr = []
            if '8000' not in current_absolute_url:
                if Profile.objects.first() is not None:
                    admin_email_address = Profile.objects.first().org_order_email.split(" ")
                else:
                    admin_email_address = 'soft@naks.ru'
                email_address_arr += admin_email_address
            if not instance.name == 'tolik_make_tests':
                send_mail(
                    'Заполнена заявка на сайте',
    """
    Заполнена заявка на сайте {url}
    Имя: {name}, Телефон: {phone}, Адрес электронной почты: {email}
    Пользователю необходимо предоставить доступ в ЭДО НАКС для заполнения заявки.
    """.format(url=current_absolute_url,
               name=instance.name,
               phone=instance.phone,
               email=instance.email),
                    settings.EMAIL_HOST_USER,
                    email_address_arr
                )
            return JsonResponse({'message': 'ok', 'order_id': instance.pk})
        else:
            return JsonResponse({'errors': form.errors})


def index(request):
    title = 'Главная страница'
    """this is mainpage view with forms handler and adapter to messages"""

    services = []

    for service_category in ServiceCategory.objects.all().order_by('number'):
        services.append({
            "pseudo": service_category.pseudo,
            "name": service_category.name,
            "services": Service.objects.filter(category=service_category).order_by("number")
        })

    content = {
        'title': title,
        'categories': ServiceCategory.objects.all().order_by('number'),
        'services': services,
        'adverts': Advert.objects.all().order_by('number') if Advert.objects.count() else None
    }
    # import pdb; pdb.set_trace()
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

def page_details(request, pk=None, content=None):

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

def details_news(request, pk=None, content=None):

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

def reset_modal_form(request):
    return render(request, 'mainapp/components/acgh-modal-feedback/component.html')

from .forms import PostSearchForm
def search_post(request):
    form = PostSearchForm(request.POST)
    results = form.search()
    context = {
        'search_results': results,
    }
    return render(request, 'mainapp/search_results.html', context)