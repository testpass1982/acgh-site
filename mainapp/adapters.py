"""Адаптер для сообщений, отправленных с помощью форм сайта"""
from django.utils import timezone
from .models import Message


class MessageModelAdapter:
    def __init__(self, data):
        self.message = Message()
        if 'send_message_button' in data:
            self.title = data['name']
            self.typeof = 'Заявка'
            self.params = {
                'attsv': 'attsv' in data,
                'attsp': 'attsv' in data,
                'attso': 'attso' in data,
                'attst': 'attst' in data,
                'nok': 'nok' in data,
                'comment': data['comment']
                }
            self.sender_email = data['email']
            self.sender_phone = data['phone']
            self.created_date = timezone.now()

        elif 'subscribe_button' in data:
            self.title = data['email']
            self.typeof = 'Подписка'
            self.params = 'Без параметров, это подписка'
            self.sender_email = data['email']
            self.sender_phone = 'не известен'
            self.created_date = timezone.now()

        elif 'ask_question' in data:
            self.title = data['name']
            self.typeof = 'Вопрос'
            self.params = data['comment']
            self.sender_email = data['email']
            self.sender_phone = data['phone']
            self.created_date = timezone.now()
        else:
            raise AttributeError(
                '{} is invalid'.format(self.__class__.__name__))

    def __str__(self):
        return '{} - {}'.format(self.title, self.typeof)

    def save_to_message(self):
        self.message.title = self.title
        self.message.typeof = self.typeof
        self.message.params = self.params
        self.message.sender_email = self.sender_email
        self.message.sender_phone = self.sender_phone
        self.message.created_date = self.created_date
        self.message.save()
        print('saved to model: ', self.message)
