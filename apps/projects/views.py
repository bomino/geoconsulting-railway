from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import DetailView, ListView

from apps.core.enums import ProjectCategory
from apps.projects.models import Project


@method_decorator(cache_page(60), name="dispatch")
class ProjectListView(ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"

    def get_queryset(self):
        qs = Project.objects.filter(published=True)
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ProjectCategory.choices
        context["current_category"] = self.request.GET.get("category", "")
        return context

    def get_template_names(self):
        if self.request.headers.get("HX-Request") == "true":
            return ["projects/_grid.html"]
        return [self.template_name]


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.filter(published=True)
