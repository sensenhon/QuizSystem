from django.urls import path
from django.conf.urls import handler404
from . import views

handler404 = views.custom_404_view

urlpatterns = [
    path('', views.home, name='home'),
    path('leaderboard', views.leaderboard_view, name='leaderboard'),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('about', views.about_view, name='about'),
    path('contact', views.contact_view, name='contact'),
    path('message/<int:id>', views.message_view, name='message'),
    path('terms', views.terms_view, name='terms'),
    path('downloads', views.downloads_view, name='downloads'),
    path('search/users', views.search_users_view, name='search_users'),
    path('blogs', views.blogs_view, name='blogs'),
    path('blogs/<str:blog_id>', views.blog_view, name='blog'),
]