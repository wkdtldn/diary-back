from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth import authenticate, login, logout
from django_redis import get_redis_connection
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Q


from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework import status, viewsets, generics, permissions
from rest_framework.views import APIView

from .models import UserModel, Follow, Diary, Comment
from .serializers import (
    UserSerializer,
    FollowSerializer,
    DiarySerializer,
    CommentSerializer,
)

from datetime import timedelta


# Other
@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({"csrftoken": csrf_token})


# active
redis_conn = get_redis_connection("default")


@login_required
def update_user_status(request):
    user_id = request.user.id
    # 유저 활성화 상태를 Redis에 저장, 만료 시간 1분
    # redis_conn.set(f"user:{user_id}:status", "active", ex=30)
    redis_conn.set(
        f"user:{user_id}:last_seen",
        timezone.localtime(timezone.now()).isoformat(),
    )
    return JsonResponse({"details": "update status"}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def check_user_status(request, user_id):
    last_seen = redis_conn.get(f"user:{user_id}:last_seen")
    print(last_seen)
    if last_seen:
        last_active_time = timezone.datetime.fromisoformat(last_seen.decode())
        time_difference = timezone.localtime(timezone.now()) - last_active_time
        if (
            time_difference.total_seconds() > 60
        ):  # 1분 이상 업데이트되지 않으면 offline 처리
            return JsonResponse({"status": False, "last_active": last_seen.decode()})
        return JsonResponse({"status": True, "last_active": last_seen.decode()})
    return JsonResponse({"status": False})


# User
class LoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({"details": "login success"}, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {"details": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        logout(request)
        return JsonResponse(
            {"details": "Successfully logged out."}, status=status.HTTP_200_OK
        )


class CheckAuthView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = UserSerializer(user)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)


class UsernameFilter(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username):
        username_exist = UserModel.objects.filter(username=username).exists()

        if username_exist:
            return Response(True)
        else:
            return Response(False)


class UserCreateView(APIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = request.data.get("username")
            if UserModel.objects.filter(username=username).exists():
                return Response(
                    {"detail": "Username already exists"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {"detail": "Invalid value"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        username = self.kwargs.get("username")
        user = get_object_or_404(UserModel, username=username)
        return user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        authenticated_user = request.user

        following = Follow.objects.filter(
            follower=authenticated_user, following=user
        ).exists()

        user_data = self.get_serializer(user).data

        user_data["following"] = following

        return Response(user_data, status=200)


class UserUpdateView(generics.UpdateAPIView):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


# Follow
class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(Q(follower=user) | Q(following=user))

    def perform_create(self, serializer):
        serializer.save(follower=self.request.user)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def followers(self, request):
        user = request.user
        followers = Follow.objects.filter(following=user).select_related("follower")
        follower_users = [follow.follower for follow in followers]
        serializer = UserSerializer(follower_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated]
    )
    def following(self, request):
        user = request.user
        following = Follow.objects.filter(follower=user).select_related("following")
        following_users = [follow.following for follow in following]
        serializer = UserSerializer(following_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["delete"],
        permission_classes=[permissions.IsAuthenticated],
    )
    def unfollow(self, request, pk=None):
        follow_instance = get_object_or_404(Follow, follower=request.user, following=pk)
        follow_instance.delete()
        return Response(
            {"detail": "Successfully unfollowed the user."},
            status=status.HTTP_204_NO_CONTENT,
        )


# Diary
class DiaryCreateView(generics.CreateAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}  # 요청 객체를 serializer의 context에 추가


class DiaryRetrieveView(generics.RetrieveAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]


class DiaryRetrieveByUserView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk=None):
        if request.user == pk:
            diaries = Diary.objects.filter(writer=pk).order_by("-date", "-time")
        else:
            diaries = Diary.objects.filter(Q(writer=pk) & Q(is_public=True))

        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DiaryFilterRetrieveView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        date = request.query_params.get("date")
        month = request.query_params.get("month")
        option = request.query_params.get("option")
        if date:
            diaries = (
                Diary.objects.filter(Q(is_public=True) | Q(writer=request.user))
                .filter(date=date)
                .order_by("-time")
            )
        if month:
            year, month = month.split("-")
            if option == "old":
                diaries = (
                    Diary.objects.filter(Q(is_public=True) | Q(writer=request.user))
                    .filter(
                        date__year=year,
                        date__month=month,
                    )
                    .order_by("date", "time")
                )
            elif option == "like":
                diaries = (
                    Diary.objects.filter(Q(is_public=True) | Q(writer=request.user))
                    .filter(
                        date__year=year,
                        date__month=month,
                    )
                    .order_by("-like")
                )
            else:
                diaries = (
                    Diary.objects.filter(Q(is_public=True) | Q(writer=request.user))
                    .filter(
                        date__year=year,
                        date__month=month,
                    )
                    .order_by("-date", "-time")
                )

        serializer = DiarySerializer(diaries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DiaryDestoryView(generics.DestroyAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]


class DiaryUpdateView(generics.UpdateAPIView):
    queryset = Diary.objects.all()
    serializer_class = DiarySerializer
    permission_classes = [permissions.IsAuthenticated]


class DiaryLikeView(APIView):
    def post(self, request, pk=None):
        diary = get_object_or_404(Diary, pk=pk)
        user = request.user
        print(user)

        if user in diary.like.all():
            diary.like.remove(user)
            response = Response(False, status=status.HTTP_200_OK)
        else:
            diary.like.add(user)
            response = Response(True, status=status.HTTP_200_OK)

        diary.save()
        return response


# Comment
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.prefetch_related("like").all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None, *args, **kwargs):
        diary_instance = get_object_or_404(Diary, id=pk)
        comments = Comment.objects.filter(diary=diary_instance).order_by("-created_at")
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

    @action(
        detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated]
    )
    def like(self, request, pk=None):
        comment = get_object_or_404(Comment, pk=pk)
        user = request.user
        print(user)

        if user in comment.like.all():
            comment.like.remove(user)
            response = Response(False, status=status.HTTP_200_OK)
        else:
            comment.like.add(user)
            response = Response(True, status=status.HTTP_200_OK)

        comment.save()
        return response
