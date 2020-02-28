from django import forms
from django.core.validators import FileExtensionValidator, validate_email
from captcha.fields import CaptchaField
import os

from .models import Post, Article, Document, Menu, Profile, OrderService


class ContentForm(forms.ModelForm):
    """form to use with fabric in news-view"""

    def __init__(self, *args, **kwargs):
        super(forms.ModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        fieldset = {
            'post_form_fields': ('title', 'tags', 'category', 'author', 'text',
                                 'created_date', 'published_date'),
            'article_form_fields': ('title', 'tags', 'author', 'text',
                                    'created_date', 'published_date'),
            'document_form_fields': ('title', 'document', 'tags',
                                     'created_date', 'uploaded_at')
        }


class PostForm(ContentForm):

    class Meta(ContentForm.Meta):
        model = Post
        fields = ContentForm.Meta.fieldset['post_form_fields']


class ArticleForm(ContentForm):

    class Meta(ContentForm.Meta):
        model = Article
        fields = ContentForm.Meta.fieldset['article_form_fields']


class DocumentForm(ContentForm):
    ALOWED_TYPES = ['jpg', 'jpeg', 'doc', 'docx', 'pdf', 'xls', 'xlsx']

    class Meta(ContentForm.Meta):
        model = Document
        fields = ContentForm.Meta.fieldset['document_form_fields']


class SendMessageForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'modal__form_input'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'class': 'modal__form_input'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'modal__form_input'}))
    params = forms.CharField(required=False, max_length=128)
    comment = forms.CharField(
        required=False, max_length=256, widget=forms.Textarea(
            attrs={'class': 'modal__form_textarea'}))
    pdata = forms.BooleanField(
        initial=True, required=True, widget=forms.CheckboxInput(
            attrs={'class': 'checkmark'}))


class SubscribeForm(forms.Form):
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(
            attrs={'class': 'main-footer__subscribe-email--input',
                   'placeholder': 'Введите e-mail'}))


class AskQuestionForm(forms.Form):
    name = forms.CharField(max_length=50, widget=forms.TextInput(
        attrs={'class': 'modal__form_input'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(
        attrs={'class': 'modal__form_input'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'modal__form_input'}))
    comment = forms.CharField(
        required=False, max_length=256, widget=forms.Textarea(
            attrs={'class': 'modal__form_textarea'}))
    pdata = forms.BooleanField(
        error_messages={
            'required': 'Вы должны принять условия обработки \
            персональных данных в соответствии с 152-ФЗ'},
        initial=True, required=True, widget=forms.CheckboxInput(
            attrs={'class': 'checkmark'}))


class DocumentSearchForm(forms.Form):
    document_name = forms.CharField(max_length=50, required=False, widget=forms.TextInput(
        attrs={'class': 'form-control',
               'placeholder': 'Введите название документа'}
    ))

class SearchRegistryForm(forms.Form):
    fio = forms.CharField(max_length=64, required=False, widget=forms.TextInput(
        attrs={'class': 'form__subject__search'}))
    work_place = forms.CharField(max_length=64, required=False, widget=forms.TextInput(
        attrs={'class': 'form__subject__search'}))

class ProfileImportForm(forms.Form):
    """form for profile import file"""
    file = forms.FileField(allow_empty_file=True, required=False)

    # def clean(self):
    #     document = self.cleaned_data.get('document', None)
    #     if not document:
    #         raise forms.ValidationError('Missing document file')
    #     try:
    #         extension = os.path.splitext(document.name)[1][1:].lower()
    #         if extension in self.ALOWED_TYPES:
    #             return document
    #         else:
    #             raise forms.ValidationError('File types is not allowed')
    #     except Exception as e:
    #         raise forms.ValidationError('Can not identify file type')

class OrderForm(forms.ModelForm):
    captcha = CaptchaField()
    class Meta:
        model = OrderService
        fields = ['name', 'phone', 'compound']
        widgets = {
                'name': forms.TextInput({
                'placeholder': "Ваше имя",
                'class': 'form-control form-control-sm',
                }),
                'phone': forms.TextInput({
                    'placeholder': '',
                    'class': 'form-control form-control-sm',
                    'type': 'text',
                }),
                # <input type="text" class="form-control form-control-sm" placeholder=""  type="text" id="phone2" required="">
            }