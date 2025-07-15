import random
import string

from django.utils import timezone

from .models import Hire, Invoice


def generate_unique_code():
    length = 8  # Set the length of the code
    chars = string.ascii_uppercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def create_invoice_for_hire(hire_id):
    hire = Hire.objects.get(uuid=hire_id)
    client = hire.job.client

    # Retrieve the client's primary address or the first available address if no primary exists
    primary_address = client.addresses.filter(primary=True).first() or client.addresses.first()
    if not primary_address:
        raise ValueError("Client must have at least one address for invoice generation.")

    currency = hire.job.country.currency or primary_address.country.currency
    # Retrieve tax details from the state associated with the address
    tax_name = primary_address.state.tax_name if primary_address.state else "Tax"
    tax_percentage = primary_address.state.tax_percentage if primary_address.state else 0

    # Create the invoice
    invoice = Invoice.objects.create(
        invoice_code=generate_unique_code(),
        client=client,
        hire=hire,
        currency=currency,
        customer_name=client.company_name,
        customer_address=primary_address.full_address,
        due_date=timezone.now() + timezone.timedelta(days=7),
        unit_price=hire.commission,
        tax_name=tax_name,
        tax_percentage=tax_percentage,
    )

    return invoice
