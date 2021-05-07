from handler.models import Operation, Customer


def create_customers_from_operations():
    operations = Operation.objects.all()
    to_insert = []
    for operation in operations:
        customer, _ = Customer.objects.get_or_create(username=operation.customer)
        

        operation = {
            'customer': row[0],
            'item': row[1],
            'total': int(row[2]),
            'quantity': int(row[3]),
            'date': row[4]
        }
        to_insert.append(operation)