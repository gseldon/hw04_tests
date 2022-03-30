from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView


urlpatterns = [
    path('', include('posts.urls', namespace='posts')),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('auth/', include('django.contrib.auth.urls')),
    path('favicon.ico', RedirectView.as_view(
        url='/static/img/fav/favicon.ico')
    ),
    path('about/', include('about.urls', namespace='about')),
]
