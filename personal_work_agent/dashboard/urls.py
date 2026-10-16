from django.urls import path
from . import views
urlpatterns = [path('',views.home,name='dashboard'),path('chat/',views.chat,name='chat'),path('tasks/',views.tasks,name='tasks'),path('documents/',views.documents,name='documents'),path('memories/',views.memories,name='memories')]
