"""
URL configuration for Athena project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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

from Apollo import views

urlpatterns = [
    path(r'', views.home, name='home'),
    path('admin/', admin.site.urls),
    path('test_search_trade/<str:name>/<str:type>/', views.search_trade_for_item, name='test_search_trade'),
    path('get_search_json_by_id/<int:id>/', views.get_search_json_by_id, name='get search by id'),
    path('view_search_result_json/<int:id>/', views.view_search_result_json, name='view search result raw json'),
    path('view_search_result/<int:id>/', views.view_search_result, name='view search result'),
    path('item_list/<str:search_string>', views.item_list, name='item_list'),
    path('bulk_exchange/<str:want>/<str:have>/', views.bulk_exchange, name='bulk_exchange'),
    path('refresh_every_5m/<str:want>/<str:have>/', views.refresh_every_5m, name='refresh_every_5m'),
    path('data_refresh/<str:type>/', views.data_refresh, name='data_refresh'),
]

