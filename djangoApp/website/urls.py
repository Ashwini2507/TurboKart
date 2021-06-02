from django.urls import path
from . import views
# from .views import PostListView, PostDetailView, PostCreateView, PostUpdateView, PostDeleteView, UserPostListView


urlpatterns = [
        path('',views.home, name="Website-Home"),
        path('about/',views.about, name='Website-About'),
        ]
