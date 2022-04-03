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
        authorized_author - авторизация от user
        authorized_not_author - авторизация от автора без постов.
        """
        self.guest_client = Client()
        self.authorized_author = Client()
        self.authorized_author.force_login(self.user01)
        self.authorized_not_author = Client()
        self.authorized_not_author.force_login(self.user02)

    def test_create_post_form(self):
        """
        Проверка создания формы.
        id последнего созданного поста ищем через дату 'pub_date' с учетом,
        что сортировка в модели может измениться.
        """
        post_count = Post.objects.count()
        form_data = {
            'text': 'Проверочный пост',
            'group': self.group.id,
        }
        response = self.authorized_author.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        last_post = Post.objects.latest('pub_date')
        self.assertRedirects(response, reverse(
            ('posts:profile'), kwargs={'username': self.user01})
        )
        # Проверим, что пост создался в базе.
        self.assertEqual(Post.objects.count(), post_count + 1)
        # Проверим, что последний созданный пост корректный.
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])

    def test_not_author_can_edit_post(self):
        """Проверка, что другой автор не может править чужой пост."""
        # В тестовой базе всего один пост от user01
        first_post_id = Post.objects.order_by('pub_date').first().id
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id,
        }
        reverse_edit = reverse(
            'posts:post_edit', kwargs={'post_id': first_post_id}
        )
        self.authorized_not_author.post(
            reverse_edit,
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.order_by('pub_date').first()
        # Проверим, изменение text не произошло
        self.assertNotEquals(edit_post.text, form_data['text'])

    def test_author_can_edit_post(self):
        """Проверка, что только автор может править пост."""
        first_post_id = Post.objects.order_by('pub_date').first().id
        form_data = {
            'text': 'Отредактированный пост',
            'group': self.group.id,
        }
        reverse_edit = reverse(
            'posts:post_edit', kwargs={'post_id': first_post_id}
        )
        self.authorized_author.post(
            reverse_edit,
            data=form_data,
            follow=True,
        )
        edit_post = Post.objects.order_by('pub_date').first()
        # Проверим, изменение text произошло
        self.assertEquals(edit_post.text, form_data['text'])
