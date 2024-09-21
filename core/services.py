from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import BorrowedBook

class BookReturnService:
    def __init__(self, borrowed_book):
        self.borrowed_book = borrowed_book

    def process_return(self):
        if not self.borrowed_book.return_date:
            self.borrowed_book.return_date = timezone.now()  
            self.borrowed_book.save()

            book = self.borrowed_book.book
            book.is_borrowed = False
            book.save()
        else:
            raise ValidationError('This book has already been returned.')
