"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from users import views as user_views

urlpatterns = [
    path('admin/', admin.site.urls),
] + i18n_patterns(
    path('', user_views.home, name='home'),
    path('signin/', user_views.signin, name='signin'),
    path('signup/', user_views.signup, name='signup'),
    path('signout/', user_views.signout, name='signout'),
    path('create-teacher/', user_views.create_teacher, name='create_teacher'),
    path('', include('curriculum.urls')),
    path('exams/', include('exams.urls')),
    path('users/', include('django.contrib.auth.urls')),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)