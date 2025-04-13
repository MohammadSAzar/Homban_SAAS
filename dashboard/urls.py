from django.urls import path, re_path

from . import views

urlpatterns = [
    # main
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # sale_file
    path('sale-files/', views.SaleFileListView.as_view(), name='sale_file_list'),
    re_path(r'sale-file/update/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileUpdateView.as_view(), name='sale_file_update'),
    re_path(r'sale-file/delete/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDeleteView.as_view(), name='sale_file_delete'),
    re_path(r'sale-file/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDetailView.as_view(), name='sale_file_detail'),
    re_path(r'sale-file/create/', views.SaleFileCreateView.as_view(), name='sale_file_create'),
    # rent_file
    path('rent-files/', views.RentFileListView.as_view(), name='rent_file_list'),
    re_path(r'rent-file/update/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileUpdateView.as_view(), name='rent_file_update'),
    re_path(r'rent-file/delete/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDeleteView.as_view(), name='rent_file_delete'),
    re_path(r'rent-file/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDetailView.as_view(), name='rent_file_detail'),
    re_path(r'rent-file/create/', views.RentFileCreateView.as_view(), name='rent_file_create'),
    # persons
    path('persons/', views.PersonListView.as_view(), name='person_list'),
    re_path(r'person/update/(?P<slug>[-\w]+)/', views.PersonUpdateView.as_view(), name='person_update'),
    re_path(r'person/delete/(?P<slug>[-\w]+)/', views.PersonDeleteView.as_view(), name='person_delete'),
    re_path(r'person/create/', views.PersonCreateView.as_view(), name='person_create'),
    # buyers
    path('buyers/', views.BuyerListView.as_view(), name='buyer_list'),
    re_path(r'buyer/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerUpdateView.as_view(), name='buyer_update'),
    re_path(r'buyer/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDeleteView.as_view(), name='buyer_delete'),
    re_path(r'buyer/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDetailView.as_view(), name='buyer_detail'),
    re_path(r'buyers/create/', views.BuyerCreateView.as_view(), name='buyer_create'),
]


