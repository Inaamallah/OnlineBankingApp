import random

def generate_account_number(length=10):
    """Generates a random numeric account number of specified length."""
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])

def format_currency(amount):
    """Formats a float as currency with 2 decimal places."""
    return "${:,.2f}".format(amount)
