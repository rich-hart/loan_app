from django.db import models
from django.contrib.auth.models import User

class Loan(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    annual_interest_rate = models.DecimalField(max_digits=6, decimal_places=3)
    loan_term_in_months = models.IntegerField()
    sharers = models.ManyToManyField(User,related_name='sharers',blank=True)


class LoanSchedule(models.Model):
    loan = models.ForeignKey(Loan, on_delete=models.CASCADE)
    month = models.IntegerField()
    remaining_balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    monthly_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
