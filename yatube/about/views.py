from django.views.generic.base import TemplateView
from django.contrib.auth import get_user_model


User = get_user_model()


class AboutAuthorView(TemplateView):
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
