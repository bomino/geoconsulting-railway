from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView

from apps.articles.models import Article


@method_decorator(cache_page(60), name="dispatch")
class ArticleListView(ListView):
    model = Article
    template_name = "articles/list.html"
    context_object_name = "articles"
    paginate_by = 9

    def get_queryset(self):
        return Article.objects.filter(published=True)


class ArticleDetailView(DetailView):
    model = Article
    template_name = "articles/detail.html"
    context_object_name = "article"

    def get_queryset(self):
        return Article.objects.filter(published=True)
