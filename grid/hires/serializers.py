from rest_framework import serializers

from grid.hires.models import Hire, Invoice, RecruiterPayment


class RecruiterPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecruiterPayment
        fields = ["amount", "due_on", "currency", "status", "percentage_of_full"]


class HireSerializer(serializers.ModelSerializer):
    recruiter_payments = serializers.SerializerMethodField()

    class Meta:
        model = Hire
        fields = [
            "uuid",
            "job",
            "base_salary",
            "payment_status",
            "recruiter",
            "join_date",
            "candidate",
            "payout",
            "commission",
            "commission_percentage",
            "recruiter_payments",
        ]

    def get_recruiter_payments(self, obj):
        payments = RecruiterPayment.objects.filter(hire=obj)
        return RecruiterPaymentSerializer(payments, many=True).data


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = [
            "uuid",
            "created_at",
            "status",
            "invoice_code",
            "client",
            "hire",
            "customer_name",
            "customer_address",
            "created_at",
            "due_date",
            "overdue",
            "currency",
            "product_name",
            "description",
            "quantity",
            "unit_price",
            "tax_name",
            "tax_percentage",
            "subtotal",
            "tax_amount",
            "total",
        ]
        read_only_fields = ["subtotal", "tax_amount", "total", "created_at", "invoice_code"]

    def get_overdue(self, obj):
        """Fetches the overdue status from the property."""
        return obj.overdue
