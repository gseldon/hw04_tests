from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Group, Post

User = get_user_model()


class StatusAuthURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create(username='test_author')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Group description'
        )

        cls.guest_urls = [
            '/',
            f'/posts/{cls.post.pk}/',
            f'/profile/{cls.user.username}/',
            f'/group/{cls.group.slug}/',

        ]

        cls.auth_urls = [
            '/create/',
            f'/posts/{cls.post.pk}/edit/',
        ]

    def setUp(self):
        # Подготовка неавторизованного клиента
        self.guest_client = Client()
        # Подготовка авторизованного клиента
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_for_guest_client(self):
        """Страницы доступные любому пользователю."""
        for urls in StatusAuthURLTests.guest_urls:
            with self.subTest():
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, 200)

    def test_deny_url_for_guest_client(self):
        """Страницы не доступны гостю."""
        for urls in StatusAuthURLTests.auth_urls:
            with self.subTest():
                response = self.guest_client.get(urls)
                self.assertEqual(response.status_code, 302)

    def test_unexsisting_page_url(self):
        """Страница /unexsisting_page/ отдает 404."""
        response = self.guest_client.get('/unexsisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_url_for_authorized_client(self):
        """
        Страницы доступные авторизованному пользователю
        и автору тестового поста.
        """
        for urls in StatusAuthURLTests.auth_urls:
            with self.subTest():
                response = self.authorized_client.get(urls)
                self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Словарь соответствия шаблона к URL
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.pk}/': 'posts/post_detail.html',
            f'/posts/{self.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
