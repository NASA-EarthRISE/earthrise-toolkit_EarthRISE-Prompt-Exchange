from django.urls import path
from . import views

urlpatterns = [
    path('access-denied/', views.access_denied, name='access_denied'),
    path('', views.home, name='home'),
    path('prompts/', views.prompt_list, name='prompt_list'),
    path('prompts/create/', views.prompt_create, name='prompt_create'),
    path('prompts/<slug:slug>/', views.prompt_detail, name='prompt_detail'),
    path('prompts/<slug:slug>/edit/', views.prompt_edit, name='prompt_edit'),
    path('prompts/<slug:slug>/delete/', views.prompt_delete, name='prompt_delete'),
    path('prompts/<slug:slug>/upvote/', views.prompt_upvote, name='prompt_upvote'),
    path('prompts/<slug:slug>/favorite/', views.prompt_favorite, name='prompt_favorite'),
    path('my-prompts/', views.user_prompts, name='user_prompts'),
]