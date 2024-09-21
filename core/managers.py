from .models import BorrowingTransaction

class BorrowingManager:
    @staticmethod
    def can_user_reserve(user):
        reserved_count = BorrowingTransaction.objects.filter(borrower=user, status='reserved').count()
        return reserved_count < 5
