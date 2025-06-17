from django.views.generic import TemplateView
#from newsletters.forms import SubscriberForm
from django.shortcuts import render


class HomePageView(TemplateView):
    """
    Render homepage with newsletter form
    """

    template_name = "pages/home.html"
    #form_class = SubscriberForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #context["form"] = SubscriberForm()
        return context


class AboutPageView(TemplateView):
    template_name = "pages/about.html"

class AppsPageView(TemplateView):
    template_name = "pages/apps.html"
class ProjectsPageView(TemplateView):
    template_name = "pages/projects.html"


class ContactPageView(TemplateView):
    template_name = "pages/contact.html"