"""
File: message_tracker.py
Email: popov.anatoly@gmail.com
Description: message tracker will track all messages
an send notifications via sms and email
"""
from abc import ABCMeta, abstractmethod
from .models import Message
from django.core.mail import send_mail


def singleton(class_):
    """decorator for classes"""
    instances = {}

    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance


@singleton
class MessageTracker:
    """object to register messages and notify observers"""
    """this must be a single instance"""

    def __init__(self):
        self.messages = []
        self.observers = [EmailNotifyer(
            'email_notifyer'), SMSNotifyer('sms_notifyer')]

    def check_messages(self):
        for message in Message.objects.all():
            if message.status == 0:
                self.messages.append(message)
                print(message, ' added to notify-list')
            else:
                print(message, ' has been already sent')
                # time.sleep(1)

    def register_observer(self, observer):
        if observer in self.observers:
            print(observer, ' already registered')
        else:
            self.observers.append(observer)
            print(observer, ' registered')

    def notify_observers(self):
        if len(self.messages) != 0:
            for observer in self.observers:
                print('Notifying ', observer)
                try:
                    observer.notify(self.messages)
                except Exception as e:
                    print(e)
        self.messages = []


class MessageNotifyer:
    """object to make notifications"""
    __metaclass__ = ABCMeta

    @abstractmethod
    def notify(self, messages):
        pass


@singleton
class EmailNotifyer(MessageNotifyer):
    """send emails"""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    # @staticmethod
    def notify(self, messages):
        for message in messages:
            if message.typeof in ('Заявка', 'Подписка', 'Вопрос'):
                print(self.name, ' got a message ', message)
                self.send_email(message)
            else:
                print(self.name, ': unknown message type')

    def send_email(self, message):
        mail_selector = {
            'Заявка': {
                'subject': 'Сообщение получено',
                'message': 'Уважаемый {}, информируем вас, что ваше сообщение \
                получено и передано в работу'
            },
            'Подписка': {
                'subject': 'Спасибо за подписку!',
                'message': '{}, благодарим Вас за подписку'
            },
            'Вопрос': {
                'subject': 'Вопрос получен',
                'message': '{}, мы получили ваш вопрос, в ближайшее время вы \
                получите ответ'
            }
        }
        if message.typeof in mail_selector.keys():
            try:
                send_mail(
                    mail_selector[message.typeof]['subject'],
                    mail_selector[message.typeof]['message'].format(
                        message.sender_email),
                    'noreply@naks-smolensk.ru',
                    ['{}'.format(message.sender_email)],
                    fail_silently=False,
                ),
                message.status = 3
                message.save()
            except Exception as e:
                print(e)
        print(self.name, ' successfully sent ', message)


@singleton
class SMSNotifyer(MessageNotifyer):
    """send sms"""

    def __init__(self, name):
        self.name = name

    def notify(self, messages):
        for message in messages:
            print(self.name, 'can not send:', message.title, '(not ready)')

    def __str__(self):
        return self.name
