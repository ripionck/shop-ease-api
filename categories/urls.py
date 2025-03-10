from django.urls import path
from . import views


app_name = 'categories'
urlpatterns = [
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('categories/<uuid:pk>/',
         views.CategoryDetailView.as_view(), name='category-detail'),
]
