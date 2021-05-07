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
                'gems': {operation.item}
            }
            customers_to_insert[customer['username']] = customer

    customers_to_insert_list = [{
        'username': customer.get('username'),
        'spent_money': customer.get('spent_money'),
        # 'gems': {gem for gem in gems if gem in customer.get('gems')}
    } for customer in customers_to_insert.values()]
    Customer.objects.bulk_create(Customer(**cust) for cust in customers_to_insert_list)

    customers = Customer.objects.all()
    for customer in customers:
        for gem in gems:
            if gem.name in customers_to_insert.get(customer.username).get('gems'):
                customer.gems.add(gem)
        customer.save()