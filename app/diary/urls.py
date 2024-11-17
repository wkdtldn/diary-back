from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

comment_router = DefaultRouter()
comment_router.register(r"comments", views.CommentViewSet, basename="comment")

follow_router = DefaultRouter()
follow_router.register(r"follow", views.FollowViewSet, basename="follow")

urlpatterns = [
    ## Other
    # Token / csrf
    path("token/csrf/", views.get_csrf_token, name="csrf-token"),
    # Search
    path("search/<str:keyword>/", views.SearchEvery.as_view(), name="search"),
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
    # update active status
    path("update-status/", views.update_user_status, name="update_user_status"),
    # check active status
    path(
        "check-status/<int:user_id>/", views.check_user_status, name="check_user_status"
    ),
    ## Diary
    # search
    path(
        "diary/filter/",
        views.DiaryFilterRetrieveView.as_view(),
        name="diary-retrieve-by-filter",
    ),
    # retrieve
    path("diary/<str:pk>/", views.DiaryRetrieveView.as_view(), name="diary-retrieve"),
    # retrieve by username
    path(
        "diary/by_user/<int:pk>",
        views.DiaryRetrieveByUserView.as_view(),
        name="diary-retrieve-by-user",
    ),
    # create
    path("diary/", views.DiaryCreateView.as_view(), name="diary-write"),
    # update
    path(
        "diary/update/<str:pk>/", views.DiaryUpdateView.as_view(), name="diary-update"
    ),
    # remove
    path(
        "diary/delete/<str:pk>/", views.DiaryDestoryView.as_view(), name="diary-delete"
    ),
    # like
    path("diary/like/<str:pk>/", views.DiaryLikeView.as_view(), name="diary-like"),
    ## Comment
    path("", include(comment_router.urls)),
    ## Follow
    path("", include(follow_router.urls)),
]
