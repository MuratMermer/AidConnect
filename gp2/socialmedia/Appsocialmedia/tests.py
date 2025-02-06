from django.test import TestCase
from .models import Profil, Post, comment
from django.contrib.auth.models import User
from django.urls import reverse

# giriş yap kayıt olma testleri -

class LoginViewTest(TestCase):
    def setUp(self):
        """Test için bir kullanıcı oluştur."""
        self.user = User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        self.login_url = reverse("login")  # 'login' görünümünün URL'sini al

    def test_login_with_valid_credentials(self):
        """Doğru bilgilerle giriş yapılabilmeli."""
        response = self.client.post(self.login_url, {
            "email": "testuser@example.com",
            "password": "securepassword123"
        })
        self.assertRedirects(response, reverse("index"))  # Anasayfaya yönlendirme kontrolü

    def test_login_with_invalid_email(self):
        """Geçersiz e-posta ile giriş yapılamamalı."""
        response = self.client.post(self.login_url, {
            "email": "wrongemail@example.com",
            "password": "securepassword123"
        })
        self.assertRedirects(response, self.login_url)  # Login sayfasına geri yönlendirme kontrolü
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Bu e-posta adresine sahip bir kullanıcı bulunamadı.")

    def test_login_with_invalid_password(self):
        """Geçersiz şifre ile giriş yapılamamalı."""
        response = self.client.post(self.login_url, {
            "email": "testuser@example.com",
            "password": "wrongpassword"
        })
        self.assertEqual(response.status_code, 200)  # Sayfa tekrar render edilmeli
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Geçersiz şifre. Lütfen tekrar deneyin.")

    def test_login_with_get_request(self):
        """GET isteğiyle login sayfası render edilmeli."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

class RegisterViewTest(TestCase):


    def setUp(self):
        """Test için bir URL belirle."""
        self.register_url = reverse("register")  # 'register' görünümünün URL'sini al

    def test_register_with_valid_data(self):
        """Geçerli bilgilerle kullanıcı kaydı yapılabilmeli."""
        response = self.client.post(self.register_url, {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "username": "testuser",
            "password": "securepassword123"
        })
        self.assertRedirects(response, "/profil/testuser")  # Profil sayfasına yönlendirme kontrolü
        self.assertTrue(User.objects.filter(username="testuser").exists())  # Kullanıcının oluşturulmuş olması gerekiyor

    def test_register_with_existing_username(self):
        """Mevcut kullanıcı adıyla kayıt yapılamamalı."""
        User.objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        response = self.client.post(self.register_url, {
            "first_name": "Test",
            "last_name": "User",
            "email": "newemail@example.com",
            "username": "testuser",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bu kullanıcı adı başka biri tarafından kullanılıyor.")

    def test_register_with_existing_email(self):
        """Mevcut e-posta adresiyle kayıt yapılamamalı."""
        User.objects.create_user(
            username="uniqueuser",
            email="testuser@example.com",
            password="securepassword123"
        )
        response = self.client.post(self.register_url, {
            "first_name": "Test",
            "last_name": "User",
            "email": "testuser@example.com",
            "username": "newuser",
            "password": "securepassword123"
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bu e-posta adresi başka biri tarafından kullanılıyor.")

    def test_register_page_renders_with_get_request(self):
        """GET isteğiyle kayıt sayfası doğru şekilde render edilmeli."""
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")
# index test

class IndexViewTest(TestCase):

    def setUp(self):
        # Test kullanıcıları ve profilleri oluşturuyoruz
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profil = Profil.objects.create(user=self.user, image="test_image.jpg", bio="Test bio")
        self.post = Post.objects.create(profil=self.profil, image="post_image.jpg", description="Test post")
        
        # Giriş yapıyoruz
        self.client.login(username="testuser", password="password123")

    def test_index_view_get(self):
        # Giriş yaptıktan sonra index sayfasının doğru şekilde render edilip edilmediğini kontrol ediyoruz.
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test post")
        self.assertTemplateUsed(response, "index.html")
    
    def test_create_post(self):
        # POST isteği ile yeni bir gönderi oluşturulması.
        response = self.client.post(reverse('index'), {
            'postbtn': 'btnpost',
            'description': 'Yeni post açıklaması',
            'image': 'new_image.jpg',
        })
        self.assertEqual(response.status_code, 302)  # Yönlendirme (redirect) olmalı
        self.assertEqual(Post.objects.count(), 2)  # Yeni bir post eklendi
        new_post = Post.objects.last()
        self.assertEqual(new_post.description, 'Yeni post açıklaması')


#model testleri
class ProfilModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profil = Profil.objects.create(user=self.user, image="test_image.jpg", bio="Test bio")

    def test_profil_creation(self):
        self.assertEqual(self.profil.user.username, "testuser")
        self.assertEqual(self.profil.bio, "Test bio")
        self.assertTrue(isinstance(self.profil, Profil))
        self.assertEqual(str(self.profil), "testuser")


class PostModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profil = Profil.objects.create(user=self.user, image="test_image.jpg", bio="Test bio")
        self.post = Post.objects.create(profil=self.profil, image="post_image.jpg", description="Test description")

    def test_post_creation(self):
        self.assertEqual(self.post.profil.user.username, "testuser")
        self.assertEqual(self.post.description, "Test description")
        self.assertTrue(isinstance(self.post, Post))
        self.assertEqual(str(self.post), "testuser")

    def test_post_likes_and_saves(self):
        another_user = User.objects.create_user(username="anotheruser", password="password456")
        another_profil = Profil.objects.create(user=another_user, image="another_image.jpg", bio="Another bio")
        
        self.post.likes.add(self.profil)
        self.post.post_save.add(another_profil)

        self.assertIn(self.profil, self.post.likes.all())
        self.assertIn(another_profil, self.post.post_save.all())


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password123")
        self.profil = Profil.objects.create(user=self.user, image="test_image.jpg", bio="Test bio")
        self.post = Post.objects.create(profil=self.profil, image="post_image.jpg", description="Test description")
        self.comment = comment.objects.create(profil=self.profil, post=self.post, comment_text="Test comment")

    def test_comment_creation(self):
        self.assertEqual(self.comment.profil.user.username, "testuser")
        self.assertEqual(self.comment.comment_text, "Test comment")
        self.assertEqual(self.comment.post, self.post)
        self.assertTrue(isinstance(self.comment, comment))
        self.assertEqual(str(self.comment), "testuser")


