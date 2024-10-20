from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
import uuid
from datetime import datetime
import os


# User
class UserModel(AbstractUser):
    name = models.CharField(max_length=100, null=False, verbose_name="name")

    image = models.ImageField(
        upload_to="profile_images/", default="profile_images/default.jpg"
    )

    groups = models.ManyToManyField(
        Group,
        related_name="customuser_set",  # 변경된 역참조 이름
        blank=True,
        help_text="The groups this user belongs to.",
        related_query_name="customuser",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="customuser_set",  # 변경된 역참조 이름
        blank=True,
        help_text="Specific permissions for this user.",
        related_query_name="customuser",
    )

    class Meta:
        ordering = ["username"]

    def save(self, *args, **kwargs):
        # 변경 전의 파일을 기록
        try:
            this = UserModel.objects.get(id=self.id)
            if this.image != self.image:
                if os.path.isfile(this.image.path):
                    if this.image == "profile_images/default.jpg":
                        pass
                    else:
                        os.remove(this.image.path)
        except UserModel.DoesNotExist:
            pass

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


# Follow
class Follow(models.Model):
    follower = models.ForeignKey(
        UserModel, related_name="following", on_delete=models.CASCADE
    )
    following = models.ForeignKey(
        UserModel, related_name="followers", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("follower", "following")
        indexes = [
            models.Index(fields=["follower", "following"]),
        ]


# Diary
class Diary(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField(blank=False, null=False)
    content = models.TextField(blank=False, null=False, default="")
    images = models.JSONField(default=list, blank=True)
    date = models.DateField()
    time = models.TimeField(auto_now_add=True)
    like = models.ManyToManyField(UserModel, related_name="liked_diaries", blank=True)
    writer = models.ForeignKey(UserModel, on_delete=models.CASCADE)

    def delete(self, *args, **kwargs):
        if self.image:
            if os.path.isfile(self.image.path):
                os.remove(self.image.path)
        super().delete(*args, **kwargs)


# Comment
class Comment(models.Model):
    id = models.AutoField(primary_key=True, null=False, blank=False)
    diary = models.ForeignKey(Diary, null=False, blank=False, on_delete=models.CASCADE)
    writer = models.ForeignKey(
        UserModel,
        null=False,
        blank=False,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True, null=False, blank=False)
    comment = models.TextField(null=False)
    like = models.ManyToManyField(UserModel, related_name="liked_comments", blank=True)

    def count_likes(self):
        return self.like.count()
