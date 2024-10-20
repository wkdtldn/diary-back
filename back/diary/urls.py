from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

comment_router = DefaultRouter()
comment_router.register(r"comments", views.CommentViewSet, basename="comment")

follow_router = DefaultRouter()
follow_router.register(r"follow", views.FollowViewSet, basename="follow")

urlpatterns = [
    path("test_request/", views.test_request, name="test"),
    ## Other
    # Token / csrf
    path("token/csrf/", views.get_csrf_token, name="csrf-token"),
    ## User
    # profile
    path("user/", views.CheckAuthView.as_view(), name="user-profile"),
    # search
    path("user/<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
    # create
    path("signup/", views.UserCreateView.as_view(), name="signup"),
    # update
    path("user/update/<int:pk>", views.UserUpdateView.as_view(), name="user-update"),
    # login
    path("login/", views.LoginView.as_view(), name="login"),
    # logout
    path("logout/", views.LogoutView.as_view(), name="logout"),
    # check username exist
    path(
        "user/check-username/<str:username>/",
        views.UsernameFilter.as_view(),
        name="username-filtering",
    ),
    ## Diary
    # search
    path("diary/", views.DiaryRetrieveView.as_view(), name="diary-retrieve"),
    # create
    path("diary/write/", views.DiaryCreateView.as_view(), name="diary-write"),
    # remove
    path("diary/remove/", views.DiaryDestoryView.as_view(), name="diary-remove"),
    # like
    path("diary/like/<str:pk>/", views.DiaryLikeView.as_view(), name="diary-like"),
    ## Comment
    path("", include(comment_router.urls)),
    ## Follow
    path("", include(follow_router.urls)),
]
