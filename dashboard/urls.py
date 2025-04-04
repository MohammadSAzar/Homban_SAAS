from django.urls import path, re_path

from . import views

urlpatterns = [
    # main
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # file
    path('sale-files/', views.SaleFileListView.as_view(), name='sale_file_list'),
    re_path(r'sale-file/update/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileUpdateView.as_view(), name='sale_file_update'),
    re_path(r'sale-file/delete/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDeleteView.as_view(), name='sale_file_delete'),
    re_path(r'sale-file/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDetailView.as_view(), name='sale_file_detail'),
    re_path(r'sale-file/create/', views.SaleFileCreateView.as_view(), name='sale_file_create'),
]


