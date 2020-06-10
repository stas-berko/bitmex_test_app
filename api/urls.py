from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api import views

urlpatterns = [
    path('orders/', views.OrderList.as_view()),
    path('orders/<str:pk>', views.OrderDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
