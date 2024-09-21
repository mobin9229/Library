from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Book, BorrowedBook

User = get_user_model()

class BookTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.book = Book.objects.create(title='Test Book', stock=1)

    def test_borrow_book(self):
        self.client.login(username='testuser', password='password123')
        response = self.client.post(f'/api/borrow-book/{self.book.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BorrowedBook.objects.count(), 1)

    def test_return_book(self):

        self.client.login(username='testuser', password='password123')
        self.client.post(f'/api/borrow-book/{self.book.id}/')


        borrowed_book = BorrowedBook.objects.first()
        response = self.client.post(f'/api/return-book/{borrowed_book.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(BorrowedBook.objects.filter(id=borrowed_book.id).first())
        self.book.refresh_from_db()
        self.assertEqual(self.book.stock, 1)  
