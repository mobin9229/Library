from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
    
class BookReview(models.Model):
    book = models.ForeignKey("Book", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('book', 'user')

class Author(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    category = models.CharField(max_length=100, default='General')
    publication_date = models.DateField(default=timezone.now)
    image = models.ImageField(upload_to='book_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title
    
    @property
    def is_available(self):
        return self.stock > 0


class BookRating(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()

    class Meta:
        unique_together = ('book', 'user')
    
    def clean(self):
        if not (1 <= self.rating <= 10):
            raise ValidationError('Rating must be between 1 and 10.')
        if BookRating.objects.filter(book=self.book, user=self.user).exists():
            raise ValidationError('You have already rated this book.')


    def save(self, *args, **kwargs):
        self.clean()  
        super().save(*args, **kwargs)  


class BorrowedBook(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='borrowed_books')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()  
    return_date = models.DateTimeField(null=True, blank=True)  

    class Meta:
        unique_together = ('user', 'book')  

    def return_book(self):
        if not self.return_date:
            self.return_date = timezone.now()  
            self.save()
        else:
            raise ValidationError('This book has already been returned.')

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"
   


class BookReturnService:
    def __init__(self, borrowed_book):
        self.borrowed_book = borrowed_book

    def process_return(self):
        
        self.borrowed_book.book.stock += 1
        self.borrowed_book.book.save()

        
        self.borrowed_book.return_book()  
        self.borrowed_book.delete()  



class Borrower(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.user.username

class BorrowingTransaction(models.Model):
    borrower = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='transactions', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name='transactions', on_delete=models.CASCADE)
    borrowed_at = models.DateTimeField(auto_now_add=True)
    returned_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, default='reserved')

    class Meta:
        unique_together = ('borrower', 'book')  


    def __str__(self):
        return f'{self.borrower} borrowed {self.book}'
    

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return f'Cart for {self.user}'

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f'{self.quantity} x {self.book.title}'

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE)
    ordered_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=255)
    is_paid = models.BooleanField(default=False)
    
    def __str__(self):
        return f'Order by {self.user} on {self.ordered_at}'