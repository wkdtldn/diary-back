from django.db.models.signals import pre_save
from django.dispatch import receiver
import boto3
from django.conf import settings
from .models import UserModel, Diary


# update 될때 기존 이미지 삭제
@receiver(pre_save, sender=UserModel)
def delete_old_image_usermodel(sender, instance, **kwargs):
    if instance.pk:
        old_instance = UserModel.objects.get(pk=instance.pk)

        if old_instance.image != "default.jpg":
            if old_instance.image != instance.image:
                s3_client = boto3.client(
                    "s3",
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME,
                )

                bucket_name = settings.AWS_STORAGE_BUCKET_NAME
                old_image_path = old_instance.image.name  # 기존 이미지 경로

                # 기존 이미지를 삭제
                try:
                    s3_client.delete_object(Bucket=bucket_name, Key=old_image_path)
                except Exception as e:
                    pass
