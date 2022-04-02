from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django import forms
from django.shortcuts import get_object_or_404
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post

POSTS_COUNT = 10
POSTS_COUNT_MAX = 13
User = get_user_model()


class TaskPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создадим запись в БД
        cls.user = User.objects.create(username='test_author')

        cls.group01 = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='Group description',
        )

        cls.group02 = Group.objects.create(
            title='test_group02',
            slug='test_slug02',
            description='Group description02',
        )
        # Создадим первый пост для автора и группы group01
        cls.post = Post.objects.create(
            author=cls.user,
            group=cls.group01,
            text='Тестовый пост 1',
        )
        # Создадим еще 12 постов для автора и группы group01
        cls.posts = (
            Post(
                author=cls.user,
                group=cls.group01,
                text=f'Текст поста {i}',
            ) for i in range(1, POSTS_COUNT_MAX)
        )
        Post.objects.bulk_create(cls.posts)

        cls.reverse_test_paginator = (
            reverse('posts:index'),
            reverse('posts:group_post', kwargs={'slug': cls.group01.slug}),
            reverse('posts:profile', kwargs={'username': cls.user}),
        )

    def setUp(self):
        # Подготовка неавторизованного клиента
        self.guest_client = Client()
        # Авторизация от автора тестовых постов
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        # Уникальным в словаре будет ключ reverse(name)
        templates_pages_names = {
            reverse('posts:index'):
                'posts/index.html',
            reverse('posts:group_post', kwargs={'slug': self.group01.slug}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.user}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}):
                'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}):
                'posts/create_post.html',
            reverse('posts:post_create'):
                'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается
        # соответствующий HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """В контексте index верный список постов."""
        response = self.authorized_client.get(reverse('posts:index'))
        context = response.context['page_obj'].object_list
        paginator = Paginator(
            Post.objects.order_by('-pub_date'), POSTS_COUNT
        )
        expect_post = list(paginator.get_page(1).object_list)
        self.assertEqual(context, expect_post)

    def test_group_posts_context(self):
        """
        В контексте group_posts верный список постов
        отфильтрованных по группе.
        """
        slug = self.group01.slug
        group = get_object_or_404(Group, slug=slug)
        response = self.authorized_client.get(
            reverse('posts:group_post', kwargs={'slug': slug})
        )
        context = list(response.context['page_obj'].object_list)
        paginator = Paginator(
            Post.objects.filter(group=group).order_by('-pub_date'), POSTS_COUNT
        )
        expect_post = list(paginator.get_page(1).object_list)
        self.assertEqual(context, expect_post)

    def test_profile_context(self):
        """
        В контексте profile верный список постов
        отфильтрованных по пользователю.
        """
        username = self.user.username
        user = get_object_or_404(User, username=username)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': username})
        )
        context = list(response.context['page_obj'].object_list)
        paginator = Paginator(
            Post.objects.filter(author=user).order_by('-pub_date'), POSTS_COUNT
        )
        expect_post = list(paginator.get_page(1).object_list)
        self.assertEqual(context, expect_post)

    def test_post_detail_context(self):
        """
        Один пост, отфильтрованный по id, на странице post_detail.
        Укажем id созданного тестового поста и проверим, что он отобразится
        на странице информации о посте
        """
        post_id = self.post.pk
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        context = response.context['post'].id
        expect_post = self.post.id
        self.assertEqual(context, expect_post)

    def test_post_edit_page_context(self):
        """Контекст post_edit верный."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_create_page_context(self):
        """Контекст post_create верный."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10."""
        for reverse_name in self.reverse_test_paginator:
            with self.subTest():
                response = self.client.get(reverse_name)
                posts_count_context = len(response.context['page_obj'])
                self.assertEqual(posts_count_context, POSTS_COUNT)

    def test_second_page_contains_three_records(self):
        """На второй странице должно быть три поста."""
        for reverse_name in self.reverse_test_paginator:
            with self.subTest():
                response = self.client.get(reverse_name, {'page': '2'})
                posts_count_context = len(response.context['page_obj'])
                self.assertEqual(
                    posts_count_context,
                    POSTS_COUNT_MAX - POSTS_COUNT
                )

    def test_post_with_group_show_on_template(self):
        """Пост с группой есть на главной странице, группы и профиля."""
        for reverse_name in self.reverse_test_paginator:
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                post = Post.objects.filter(
                    group=self.group01
                ).order_by('-pub_date')[0]
                posts = response.context['page_obj'].object_list
                self.assertTrue(post in posts)

    def test_group02_has_no_post_group01(self):
        """
        На странице второй группы нет постов первой группы.
        Так как постов для второй группы не создается в фикстурах,
        то context должен выдать пустой object_list.
        """
        response = self.authorized_client.get(
            reverse('posts:group_post', kwargs={'slug': self.group02.slug})
        )
        count_posts_group02 = len(response.context['page_obj'].object_list)
        self.assertEqual(count_posts_group02, 0)
