from django.contrib import admin
from django.urls import path
from duty import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.home, name='home'),

    path('shuffle-duty/<int:shift_id>/', views.shuffle_duty, name='shuffle-duty'),
    path('toggle-shift-lock/<int:shift_id>/', views.toggle_shift_lock, name='toggle-shift-lock'),
]