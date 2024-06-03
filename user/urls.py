from django.urls import path
from user import views as user_view

urlpatterns = [
    path('signup/', user_view.SignupView.as_view(), name='signup'),
    path('login/', user_view.LoginView.as_view(), name='login'),
    path('token/refresh/', user_view.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('search/', user_view.UserSearchView.as_view(), name='user-search'),
    path('friend-requests/', user_view.FriendRequestView.as_view(http_method_names=['get', 'post']), name='friend-request-list'),
    path('friend-requests/<int:pk>/', user_view.FriendRequestView.as_view(http_method_names=['patch']), name='friend-request-detail'),
]
