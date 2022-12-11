from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('call_api', views.call_api, name='call_api'),
    path('display_dataset/<str:dataset_filename>', views.display_dataset, name='display_dataset'),
    path('display_all_datasets', views.display_all_datasets, name='display_all_datasets'),
    path('value_counter', views.value_counter, name='value_counter'),
]