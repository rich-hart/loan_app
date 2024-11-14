from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .serializers import LoanSerializer, LoanScheduleSerializer
from .models import Loan, LoanSchedule
from .utils import amortize_loan, interest_payment 


class IsShared(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """

    def has_object_permission(self, request, view, obj):
        return request.user in obj.sharers.all()


class LoanViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Loan.objects.all()
    serializer_class = LoanSerializer
    permission_classes = [permissions.IsAuthenticated & IsShared]
    filterset_fields = ['owner']

    def get_queryset(self):
        user = self.request.user
        return Loan.objects.filter(sharers__email=user.email)
   
    def perform_create(self, serializer):
        instance = serializer.save()
        instance.sharers.add(instance.owner)

        P = float(instance.amount)
        r = float(instance.annual_interest_rate) / (100.00 * 12.00)
        n = instance.loan_term_in_months
        A =  amortize_loan(P, r, n)
        schedule_data = [
            {
                "month": 0,
                "remaining_balance": P,
                "monthly_payment": A,
            }
        ]
        for i in range(1, n):
            month = i
            remaining_balance = schedule_data[i-1]["remaining_balance"] * (1.0 + r) - A
            monthly_payment = A
            schedule_data.append({
                "month": month,
                "remaining_balance": remaining_balance,
                "monthly_payment": monthly_payment,
            })

        for s in schedule_data:
            loan_schedule = LoanSchedule(**s, loan=instance)
            loan_schedule.save()

class LoanScheduleViewSet(viewsets.ModelViewSet):
    queryset = LoanSchedule.objects.all()
    serializer_class = LoanScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['loan']
    http_method_names = ['get', 'head', 'options']

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        loan_schedule = self.get_object()

        summary = {
            'month': loan_schedule.month,
            "current_principal_balance": float(loan_schedule.remaining_balance),
            'aggregate_principal': 0.0,
            'aggregate_interest': 0.0,
        }

        for i in range(loan_schedule.month):
            P = float(loan_schedule.remaining_balance)
            r = float(loan_schedule.loan.annual_interest_rate)/(100.00)
            n = 12
            interest = interest_payment(P, r, n)
            principal = float(loan_schedule.monthly_payment) - interest
            summary['aggregate_interest'] = summary['aggregate_interest'] + interest
            summary['aggregate_principal'] = summary['aggregate_principal'] + principal
        summary['current_principal_balance'] = f"{summary['current_principal_balance']:.2f}"
        summary['aggregate_principal'] = f"{summary['aggregate_principal']:.2f}"
        summary['aggregate_interest'] = f"{summary['aggregate_interest']:.2f}"
        return Response(summary)
         
