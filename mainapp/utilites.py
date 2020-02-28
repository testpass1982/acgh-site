# from django.core.paginator import Paginator
# from django.http import HttpRequest as request


class UrlMaker:
    """makes next and prev url to current url"""
    next_url = ''
    prev_url = ''

    def __init__(self, url, paginated_records):
        self.current = url
        self.paginated = paginated_records
        if 'search' in self.current:
            self.url_param = '&page='
        else:
            self.url_param = '?page='

    def make_next_url(self):
        if self.paginated.has_next():
            if self.url_param in self.current:
                self.next_url = self.current.replace(
                    self.url_param+str(self.paginated.number), self.url_param+'{}'.format(str(self.paginated.number+1)))
            else:
                self.next_url = self.current + \
                    self.url_param+'{}'.format(self.paginated.number+1)
        else:
            self.next_url = None
        return self.next_url

    def make_prev_url(self):
        if self.paginated.number == 1:
            self.prev_url = None
        else:
            self.prev_url = self.current.replace(
                self.url_param+str(self.paginated.number), self.url_param+'{}'.format(self.paginated.number-1))
        return self.prev_url

    def urls_dict(self):
        return {'next_url': self.next_url, 'prev_url': self.prev_url}

#*** import fields ***
from django.db.models.fields.related import ForeignObjectRel, RelatedField
#*** import end ***

def is_simple_editable_field(field):
    return (
            field.editable
            and not field.primary_key
            and not isinstance(field, (ForeignObjectRel, RelatedField))
    )

def update_from_dict(instance, attrs):
    allowed_field_names = {
        f.name for f in instance._meta.get_fields()
        if is_simple_editable_field(f)
    }

    for attr, val in attrs.items():
        if attr in allowed_field_names:
            setattr(instance, attr, val)

    instance.save()
