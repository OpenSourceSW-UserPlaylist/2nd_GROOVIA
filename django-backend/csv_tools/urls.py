from django.urls import path
from . import views

urlpatterns = [
    # path('songs/save/', views.save_song, name='save_song'),
    path('songs/', views.process_and_send_recommendations, name='get_songs'),
]