from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User, Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Подготовка фикстур для теста.
        Создадим автора, одну группу и один тестовый пост.
        """
        super().setUpClass()
        cls.user01 = User.objects.create(username='test_author01')
        cls.user02 = User.objects.create(username='test_author02')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Group description',
        )

        cls.post = Post.objects.create(
            author=cls.user01,
            group=cls.group,
            text='Тестовый пост 1',
        )

    def setUp(self):
        """
        Подготовка тестового веб клиента
        guest_client - гостевой
        authorized_client - авторизация от user.
        """
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user01)

    def test_create_post_form(self):
        """Проверка создания формы."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Проверочный пост',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        post_last_id = post_count + 1

        # Проверим, что после создания формы происходит
        # перенаправление на страницу автора
        self.assertRedirects(response, reverse(
            ('posts:profile'), kwargs={'username': self.user01})
        )
        self.assertEqual(Post.objects.count(), post_last_id)
        # Проверим, что последний созданный пост корректный
        self.assertTrue(
            Post.objects.filter(
                id=post_last_id,
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )

    def test_edit_post(self):
        """
        Проверка на редактирование поста.
        Только автор может править пост.
        """
        # В тестовой базе всего один пост от user01
        post_id = 1
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id,
        }
        reverse_edit = reverse('posts:post_edit', kwargs={'post_id': post_id})
        # Авторизуемся не под автором первого поста
        # и попробуем его отредактировать
        self.authorized_client.force_login(self.user02)
        self.authorized_client.post(
            reverse_edit,
            data=form_data,
            follow=True,
        )
        self.assertFalse(
            Post.objects.filter(
                id=post_id,
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )
        # Авторизуемся под автором первого поста
        # и попробуем его отредактировать
        self.authorized_client.force_login(self.user01)
        self.authorized_client.post(
            reverse_edit,
            data=form_data,
            follow=True,
        )
        self.assertTrue(
            Post.objects.filter(
                id=post_id,
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )
