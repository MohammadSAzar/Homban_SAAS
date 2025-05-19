from django.urls import path, re_path

from . import views

# urlpatterns = [
#     # main
#     path('', views.home_view, name='home'),
#     path('home/', views.home_view, name='home'),
#     path('dashboard/', views.dashboard_view, name='dashboard'),
#     # sale_file
#     path('sale-files/', views.SaleFileListView.as_view(), name='sale_file_list'),
#     re_path(r'sale-file/update/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileUpdateView.as_view(), name='sale_file_update'),
#     re_path(r'sale-file/delete/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDeleteView.as_view(), name='sale_file_delete'),
#     re_path(r'sale-file/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDetailView.as_view(), name='sale_file_detail'),
#     re_path(r'sale-file/create/', views.SaleFileCreateView.as_view(), name='sale_file_create'),
#     # rent_file
#     path('rent-files/', views.RentFileListView.as_view(), name='rent_file_list'),
#     re_path(r'rent-file/update/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileUpdateView.as_view(), name='rent_file_update'),
#     re_path(r'rent-file/delete/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDeleteView.as_view(), name='rent_file_delete'),
#     re_path(r'rent-file/(?P<slug>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDetailView.as_view(), name='rent_file_detail'),
#     re_path(r'rent-file/create/', views.RentFileCreateView.as_view(), name='rent_file_create'),
#     # locations
#     path('locations/', views.LocationListView.as_view(), name='location_list'),
#     re_path(r'location/province/update/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.ProvinceUpdateView.as_view(), name='province_update'),
#     re_path(r'location/city/update/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.CityUpdateView.as_view(), name='city_update'),
#     re_path(r'location/sub_district/update/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.SubDistrictUpdateView.as_view(), name='sub_district_update'),
#     re_path(r'location/district/update/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.DistrictUpdateView.as_view(), name='district_update'),
#     re_path(r'location/province/delete/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.ProvinceDeleteView.as_view(), name='province_delete'),
#     re_path(r'location/city/delete/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.CityDeleteView.as_view(), name='city_delete'),
#     re_path(r'location/sub_district/delete/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.SubDistrictDeleteView.as_view(), name='sub_district_delete'),
#     re_path(r'location/district/delete/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.DistrictDeleteView.as_view(), name='district_delete'),
#     re_path(r'location/province/create/', views.ProvinceCreateView.as_view(), name='province_create'),
#     re_path(r'location/city/create/', views.CityCreateView.as_view(), name='city_create'),
#     re_path(r'location/district/create/', views.DistrictCreateView.as_view(), name='district_create'),
#     re_path(r'location/sub_district/create/', views.SubDistrictCreateView.as_view(), name='sub_district_create'),
#     # persons
#     path('persons/', views.PersonListView.as_view(), name='person_list'),
#     re_path(r'person/update/(?P<pk>[-\w]+)/', views.PersonUpdateView.as_view(), name='person_update'),
#     re_path(r'person/delete/(?P<pk>[-\w]+)/', views.PersonDeleteView.as_view(), name='person_delete'),
#     re_path(r'person/create/', views.PersonCreateView.as_view(), name='person_create'),
#     # buyers
#     path('buyers/', views.BuyerListView.as_view(), name='buyer_list'),
#     re_path(r'buyer/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerUpdateView.as_view(), name='buyer_update'),
#     re_path(r'buyer/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDeleteView.as_view(), name='buyer_delete'),
#     re_path(r'buyer/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDetailView.as_view(), name='buyer_detail'),
#     re_path(r'buyers/create/', views.BuyerCreateView.as_view(), name='buyer_create'),
#     # renters
#     path('renters/', views.RenterListView.as_view(), name='renter_list'),
#     re_path(r'renter/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterUpdateView.as_view(), name='renter_update'),
#     re_path(r'renter/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterDeleteView.as_view(), name='renter_delete'),
#     re_path(r'renter/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterDetailView.as_view(), name='renter_detail'),
#     re_path(r'renters/create/', views.RenterCreateView.as_view(), name='renter_create'),
#     # tasks
#     path('tasks/for-files/', views.TaskFPListView.as_view(), name='task_fp_list'),
#     path('tasks/for-customers/', views.TaskCPListView.as_view(), name='task_cp_list'),
#     path('tasks/dual/', views.TaskBTListView.as_view(), name='task_bt_list'),
#     path('tasks/boss/under-review/', views.TaskBossURListView.as_view(), name='task_bs_ur_list'),
#     path('tasks/boss/open/', views.TaskBossOPListView.as_view(), name='task_bs_op_list'),
#     path('tasks/boss/close/', views.TaskBossCLListView.as_view(), name='task_bs_cl_list'),
#     re_path(r'task/update/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.TaskUpdateView.as_view(), name='task_update'),
#     re_path(r'task/result/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.TaskResultView.as_view(), name='task_result'),
#     re_path(r'task/detail/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.TaskDetailView.as_view(), name='task_detail'),
#     re_path(r'task/delete/(?P<pk>[-\w]+)/(?P<slug>[-\w]+)/', views.TaskDeleteView.as_view(), name='task_delete'),
#     re_path(r'task/create/', views.TaskCreateView.as_view(), name='task_create'),
# ]

urlpatterns = [
    # main
    path('', views.home_view, name='home'),
    path('home/', views.home_view, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    # sale_file
    path('sale-files/', views.SaleFileListView.as_view(), name='sale_file_list'),
    re_path(r'sale-file/update/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileUpdateView.as_view(), name='sale_file_update'),
    re_path(r'sale-file/delete/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDeleteView.as_view(), name='sale_file_delete'),
    re_path(r'sale-file/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.SaleFileDetailView.as_view(), name='sale_file_detail'),
    re_path(r'sale-file/create/', views.SaleFileCreateView.as_view(), name='sale_file_create'),
    # rent_file
    path('rent-files/', views.RentFileListView.as_view(), name='rent_file_list'),
    re_path(r'rent-file/update/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileUpdateView.as_view(), name='rent_file_update'),
    re_path(r'rent-file/delete/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDeleteView.as_view(), name='rent_file_delete'),
    re_path(r'rent-file/(?P<pk>[-\w]+)/(?P<unique_url_id>[-\w]+)/', views.RentFileDetailView.as_view(), name='rent_file_detail'),
    re_path(r'rent-file/create/', views.RentFileCreateView.as_view(), name='rent_file_create'),
    # locations
    path('locations/', views.LocationListView.as_view(), name='location_list'),
    re_path(r'location/province/update/(?P<pk>[-\w]+)/', views.ProvinceUpdateView.as_view(), name='province_update'),
    re_path(r'location/city/update/(?P<pk>[-\w]+)/', views.CityUpdateView.as_view(), name='city_update'),
    re_path(r'location/sub_district/update/(?P<pk>[-\w]+)/', views.SubDistrictUpdateView.as_view(), name='sub_district_update'),
    re_path(r'location/district/update/(?P<pk>[-\w]+)/', views.DistrictUpdateView.as_view(), name='district_update'),
    re_path(r'location/province/delete/(?P<pk>[-\w]+)/', views.ProvinceDeleteView.as_view(), name='province_delete'),
    re_path(r'location/city/delete/(?P<pk>[-\w]+)/', views.CityDeleteView.as_view(), name='city_delete'),
    re_path(r'location/sub_district/delete/(?P<pk>[-\w]+)/', views.SubDistrictDeleteView.as_view(), name='sub_district_delete'),
    re_path(r'location/district/delete/(?P<pk>[-\w]+)/', views.DistrictDeleteView.as_view(), name='district_delete'),
    re_path(r'location/province/create/', views.ProvinceCreateView.as_view(), name='province_create'),
    re_path(r'location/city/create/', views.CityCreateView.as_view(), name='city_create'),
    re_path(r'location/district/create/', views.DistrictCreateView.as_view(), name='district_create'),
    re_path(r'location/sub_district/create/', views.SubDistrictCreateView.as_view(), name='sub_district_create'),
    # persons
    path('persons/', views.PersonListView.as_view(), name='person_list'),
    re_path(r'person/update/(?P<pk>[-\w]+)/', views.PersonUpdateView.as_view(), name='person_update'),
    re_path(r'person/delete/(?P<pk>[-\w]+)/', views.PersonDeleteView.as_view(), name='person_delete'),
    re_path(r'person/create/', views.PersonCreateView.as_view(), name='person_create'),
    # buyers
    path('buyers/', views.BuyerListView.as_view(), name='buyer_list'),
    re_path(r'buyer/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerUpdateView.as_view(), name='buyer_update'),
    re_path(r'buyer/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDeleteView.as_view(), name='buyer_delete'),
    re_path(r'buyer/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.BuyerDetailView.as_view(), name='buyer_detail'),
    re_path(r'buyers/create/', views.BuyerCreateView.as_view(), name='buyer_create'),
    # renters
    path('renters/', views.RenterListView.as_view(), name='renter_list'),
    re_path(r'renter/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterUpdateView.as_view(), name='renter_update'),
    re_path(r'renter/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterDeleteView.as_view(), name='renter_delete'),
    re_path(r'renter/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.RenterDetailView.as_view(), name='renter_detail'),
    re_path(r'renters/create/', views.RenterCreateView.as_view(), name='renter_create'),
    # tasks
    path('tasks/for-files/', views.TaskFPListView.as_view(), name='task_fp_list'),
    path('tasks/for-customers/', views.TaskCPListView.as_view(), name='task_cp_list'),
    path('tasks/dual/', views.TaskBTListView.as_view(), name='task_bt_list'),
    path('tasks/boss/under-review/', views.TaskBossURListView.as_view(), name='task_bs_ur_list'),
    path('tasks/boss/open/', views.TaskBossOPListView.as_view(), name='task_bs_op_list'),
    path('tasks/boss/close/', views.TaskBossCLListView.as_view(), name='task_bs_cl_list'),
    re_path(r'task/update/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.TaskUpdateView.as_view(), name='task_update'),
    re_path(r'task/result/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.TaskResultView.as_view(), name='task_result'),
    re_path(r'task/detail/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.TaskDetailView.as_view(), name='task_detail'),
    re_path(r'task/delete/(?P<pk>[-\w]+)/(?P<code>[-\w]+)/', views.TaskDeleteView.as_view(), name='task_delete'),
    re_path(r'task/create/', views.TaskCreateView.as_view(), name='task_create'),
]





