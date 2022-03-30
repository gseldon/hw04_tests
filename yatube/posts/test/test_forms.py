from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User, Group, Post


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим фикстуры для теста в БД
        cls.user = User.objects.create(username='test_author')

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Group description'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group,
            text='Тестовый пост 1',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

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
            follow=True
        )
        # Проверим, что после создания формы происходит
        # перенаправляете на страницу автора
        self.assertRedirects(response, reverse(
            ('posts:profile'), kwargs={'username': self.user})
        )
        # Проверим, что пост создался, через увеличение
        # количества постов
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверим, что пост создался корректно
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
            ).exists()
        )
