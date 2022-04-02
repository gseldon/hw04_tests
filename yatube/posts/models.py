from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def delete_user():
    User.objects.get_or_create(username='anonymous')[0]


class Group(models.Model):
    """Описание модели группы"""
    title = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField(max_length=200)
    slug = models.SlugField(unique=True)

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """
    Post описывает модель БД для работы с постами.
    author:
        связь с таблицей пользователей.
        При удалении выполенении функции выставления anonymous в поле
        пользователя. Реализовал, для тестирования функционала действий при
        удалении.
    group:
        связь с таблицей групп.
        При удалении группы, в постах просто ставим NULL
    """
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста',
    )
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.SET(delete_user),
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )

    def __str__(self) -> str:
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
