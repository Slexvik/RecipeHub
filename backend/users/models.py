from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from users.validators import ValidateUsername


class User(ValidateUsername, AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('first_name', 'last_name', 'username')

    email = models.EmailField(
        verbose_name='Электронная почта',
        unique=True,
        max_length=settings.MAX_LENGTH_EMAIL,
    )
    username = models.CharField(
        unique=True,
        max_length=settings.MAX_LENGTH_IN_NAME,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_name',
            ),
            models.CheckConstraint(
                check=~models.Q(username='me'),
                name='name_not_me',
            ),
        ]

    def __str__(self):
        return self.username


class Follow(models.Model):

    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('following')),
                name='no_self_subscription',
            ),
        ]

        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'Подписчик: {self.follower} подписан на {self.following}'
