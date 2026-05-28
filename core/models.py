from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# ModelBaseClass を作成し、created_at / updated_at を共通化
class ModelBaseClass(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    class Meta:
        abstract = True

class Plan(ModelBaseClass):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='plans',
        null=False,
        blank=False,
    )
    plan_name = models.CharField(max_length=100)
    plan_start_date = models.DateTimeField()
    plan_end_date = models.DateTimeField()

    def __str__(self):
        return self.plan_name
    
class Task(ModelBaseClass):
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='tasks',
        null=False,
        blank=False
    )
    genre=models.CharField(max_length=100)
    title=models.CharField(max_length=100)
    is_active=models.BooleanField(default=False)
    task_start_date=models.DateTimeField()
    task_end_date=models.DateTimeField()

    def __str__(self):
        return self.title
    
class TaskDetail(ModelBaseClass):

    EVALUATION_CHOICES = [
        (0, '未実施'),
        (1, '分からない'),
        (2, 'なんとなく'),
        (3, '理解した'),
    ]

    task = models.OneToOneField(
        Task,
        on_delete=models.CASCADE,
        related_name='task_detail'
    )
    
    evaluation=models.IntegerField(
        default=0,
        null=False,
        choices=EVALUATION_CHOICES
    )
    memo=models.TextField(null=True)

class Link(ModelBaseClass):
    # task_detail=models.ForeignKey(
    #     TaskDetail,
    #     on_delete=models.CASCADE,
    #     related_name='links',
    #     null=False,
    #     blank=False
    # )
    plan = models.ForeignKey(
        Plan,
        on_delete=models.CASCADE,
        related_name='links',
        null=False,
        blank=False
    )
    url = models.TextField()
    link_name = models.TextField()

    def __str__(self):
        return self.url
    
class Comment(ModelBaseClass):
    task_detail=models.ForeignKey(
        TaskDetail,
        on_delete=models.CASCADE,
        related_name='comments',
        null=False,
        blank=False
    )

    #コメント内容の文字数制限に柔軟に対応できるよう、comment フィールドを CharField から TextField に変更
    #comment = models.CharField()
    comment = models.TextField()

    def __str__(self):
        return self.comment
