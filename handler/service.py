from django.db.models import QuerySet

from handler.models import Operation, Customer, Gem


def create_customers_and_gems_from_operations(operations):
    Gem.objects.all().delete()
    Customer.objects.all().delete()

    gems_set = set()
    for operation in operations:
        gems_set.add(operation.item)
    gems_to_insert = [{
        'name': gem
    } for gem in gems_set]
    Gem.objects.bulk_create(Gem(**gem) for gem in gems_to_insert)

    gems = Gem.objects.all()
    customers_to_insert = dict()
    for operation in operations:
        customer = customers_to_insert.get(operation.customer)
        if customer:
            customer['spent_money'] = customer['spent_money'] + operation.total
            customer['gems'].add(operation.item)
        else:
            customer = {
                'username': operation.customer,
                'spent_money': operation.total,
                'gems': set(operation.item)
            }
            customers_to_insert[customer['username']] = customer
    # print(customers_to_insert)
    # customers_to_insert_list = [{
    #     'name': customer.get('username'),
    #     'spent_money': customer.get('username'),
    #     'gems': {gem for gem}
    # } for customer in customers_to_insert]
    # print(Customer.objects.bulk_create(Customer(**cust) for cust in customers_to_insert_list))



    # Operation(**operation)
    # for operation in to_insert

    # customers_to_insert = {}

    # customer = {
    #     'username': operation.customer,
    #     'spent_money':
    # }

    # operation = {
    #     'customer': row[0],
    #     'item': row[1],
    #     'total': int(row[2]),
    #     'quantity': int(row[3]),
    #     'date': row[4]
    # }
