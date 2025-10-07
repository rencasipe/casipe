from django.views.generic import TemplateView

# Create your views here.
class AppsPageView(TemplateView):
    template_name = "apps/apps.html"