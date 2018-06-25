"""frontend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from search.views import searchbyentity, search, add, searchbytwoentities, showEntity, dashboard, searchTwoEntities,fsearch
from ETL.views import index, entity, relation


urlpatterns = [
    path(r'admin/', admin.site.urls),

    path(r'ETL/', index),
    path(r'ETL/upload1/', entity),
    path(r'ETL/upload2/', relation),

    # path(r'search/', index),
    path(r'search/', searchbyentity),
    path(r'searchbytwoentities/', searchbytwoentities),
    path(r'dashboard/', dashboard),
    path(r'search1/', search),
    path(r'search2/', add),
    path(r'search3/', searchTwoEntities),
    path(r'search4/', showEntity),
    path(r'fsearch/', fsearch)
]
