import datetime
from haystack import indexes
from mainapp.models import Post

class PostIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(model_attr="text", document=True, use_template=True)
    title = indexes.CharField(use_template=True)

    def get_model(self):
        return Post

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(created_date__lte=datetime.datetime.now())