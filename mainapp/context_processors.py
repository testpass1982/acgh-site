from .models import Document
from .models import Profile, Service, Post, SiteConfiguration, Component, Partner, Attestat
from .forms import ProfileImportForm, OrderForm
import random
from django.template import Context, Template
from django.shortcuts import render, get_object_or_404
from .models import Document, Staff
from django.utils.termcolors import colorize
from .classes import SiteComponent


def random_documents(request):
    all_documents = Document.objects.all()
    if len(all_documents) > 3:
        all_document_pks = [doc.pk for doc in all_documents]
        documents = []
        for i in range(0, 5):
            try:
                random_document = Document.objects.get(pk=random.choice(all_document_pks))
                # import pdb; pdb.set_trace()
                if random_document not in documents:
                    documents.append(random_document)
            except Exception as e:
                return {'random_documents': [e]}
        return {'random_documents': documents}
    else:
        return {'random_documents': ['Добавьте больше документов в базу данных']}


def basement_news(request):
    try:
        basement_news = Post.objects.filter(
            publish_in_basement=True).order_by(
                '-published_date')[:3]
        return {'basement_news': basement_news}
    except Exception as e:
        print('ERROR', e)


def profile_chunks(request):
    profile = Profile.objects.first()
    return {'profile': profile}


def services(request):

    services = Service.objects.all().order_by('number')
    all_services = []
    for s in services:
        if s.parent is None:
            all_services.append({'title': s.title, 'pk': s.pk, 'descendants': Service.objects.filter(parent=s)})
        else:
            continue
    # import pdb; pdb.set_trace()
    return {'all_services': all_services}



def profile_import(request):
    profile_import_form = ProfileImportForm()
    return {'profile_import_form': profile_import_form}


def site_configuration(request):
    try:
        site = SiteConfiguration.objects.filter(activated=True)
        bd_components = Component.objects.filter(configuration=site[0].pk).order_by('number')
        site_components = [SiteComponent(component) for component in bd_components]
        # import pdb; pdb.set_trace()
        return {
                'site': {
                    'components': site_components,
                    'font_url': site[0].font.font_url,
                    'font_family': site[0].font.title,
                    }
                }
    except Exception as e:
        print (colorize('###---> SITE CONFIGURATION ERROR: {}'.format(e), bg='red'))
        return {'site': {'components': None}}

def partners(request):
    try:
        partners = Partner.objects.all().order_by('number')
    except Exception as e:
        print('PARTNERS ERROR:', e)
        partners = [{'partner': {'title': 'Загрузите партнеров в админку'}}]
    # import pdb; pdb.set_trace()
    return {'partners': partners}


def order_form(request):
    order_form = OrderForm()
    return {'order_form': order_form}


def org_staff(request):
    if Staff.objects.count() > 0:
        return {
            "staff": Staff.objects.all().order_by('priority')
        }
    else:
        return {
            "staff": None
        }


def attestats(request):
    if Attestat.objects.count() > 0:
        return {
            "attestats": Attestat.objects.all().order_by('number')
        }
    else:
        return {
            "attestats": None
        }

