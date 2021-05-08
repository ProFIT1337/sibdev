from handler.models import Customer, Gem, Operation


def clear_db():
    """Удаляет все объекты из базы данных(Customer, Gem, Operation)"""
    Gem.objects.all().delete()
    Customer.objects.all().delete()
    Operation.objects.all().delete()


def create_gems(operations):
    """Создаёт объекты камней(Gem)"""
    gems_set = set()
    for operation in operations:
        gems_set.add(operation.item)
    gems_to_insert = [{
        'name': gem
    } for gem in gems_set]
    Gem.objects.bulk_create(Gem(**gem) for gem in gems_to_insert)


def create_customers(operations):
    """
        Создаёт покупателей(Customer).
        Возвращает словарь созданных покупателей.
    """
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
    } for customer in customers_to_insert.values()]

    Customer.objects.bulk_create(Customer(**customer) for customer in customers_to_insert_list)
    return customers_to_insert


def get_top_customers(customers):
    """Возвращает список из 5 покупателей, потративших наибольшую сумму"""
    top_customers = sorted(customers, key=lambda customer: customer.spent_money, reverse=True)
    return top_customers[:5]


def add_gems_to_customers(customers_dict):
    """Добавляет купленные пользователями камни в поле gems модели Customer"""
    gems = Gem.objects.all()
    customers = Customer.objects.all()
    top_customers = get_top_customers(customers)
    customers_to_insert = []
    for customer in customers:
        for gem in gems:
            if gem.name in customers_dict.get(customer.username).get('gems'):
                customer.gems.add(gem)
        if customer in top_customers:
            customer.is_in_top_five = True
            customers_to_insert.append(customer)
    Customer.objects.bulk_update(customers_to_insert, fields=('is_in_top_five',))


def mark_gems_to_display():
    """Проверяет все камни(Gem) и изменяет поле is_visible, если этот камень надо отобразить в результатах"""
    gems = Gem.objects.all()
    gems_to_insert = []
    for gem in gems:
        if gem.customers.filter(is_in_top_five=True).count() > 1:
            gem.is_visible = True
            gems_to_insert.append(gem)
    Gem.objects.bulk_update(gems_to_insert, fields=('is_visible',))


def create_customers_and_gems_from_operations(operations):
    """Создаёт объекты покупателей(Customer) и камней(Gem) на основе операций(Operation)"""
    create_gems(operations)
    customers_dict = create_customers(operations)
    add_gems_to_customers(customers_dict)
    mark_gems_to_display()
