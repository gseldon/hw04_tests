from django.test import TestCase, Client


class StaticURLTests(TestCase):
    def setUp(self):
        # Устанавливаем данные для тестирования
        # Создаём экземпляр клиента. Он неавторизован.
        self.guest_client = Client()

    def test_homepage(self):
        """
        Домашняя страница открывается.
        """
        # Создаем экземпляр клиента
        guest_client = Client()
        # Делаем запрос к главной странице и проверяем статус
        response = guest_client.get('/')
        # Утверждаем, что для прохождения теста код должен быть равен 200
        self.assertEqual(response.status_code, 200)
