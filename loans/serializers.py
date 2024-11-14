from rest_framework import serializers

from .models import Loan, LoanSchedule


class LoanSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Loan
        fields = '__all__'

class LoanScheduleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = LoanSchedule
        fields = '__all__'

    
