
from django.urls import path
from . import views

urlpatterns = [
    path('shuffle-duty/<int:shift_id>/', views.shuffle_duty, name='shuffle-duty'),
    path('toggle-shift-lock/<int:shift_id>/', views.toggle_shift_lock, name='toggle-shift-lock'),
]

from django.urls import path
from . import views

urlpatterns = [
    path('shuffle-duty/<int:shift_id>/', views.shuffle_duty, name='shuffle-duty'),
    path('toggle-shift-lock/<int:shift_id>/', views.toggle_shift_lock, name='toggle-shift-lock'),

]