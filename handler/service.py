from handler.models import Customer, Gem, Operation


def clear_db():
    """Удаляет все объекты из базы данных(Customer, Gem, Operation)"""
    Gem.objects.all().delete()
    Customer.objects.all().delete()
    Operation.objects.all().delete()


def get_top_customers(customers):
    """Возвращает список из 5 покупателей, потративших наибольшую сумму"""
    top_customers = sorted(customers, key=lambda customer: customer.spent_money, reverse=True)
    return top_customers[:5]


def add_gems_to_customers(customers, customers_dict):
    """Добавляет купленные пользователями камни в поле gems модели Customer"""
    gems = Gem.objects.all()
    top_customers = get_top_customers(customers)
    customers_to_insert = []
    gems_to_customer_links = []
    customers = Customer.objects.all()
    for customer in customers:
        for gem in gems:
            if gem.name in customers_dict.get(customer.username).get('gems'):
                gems_to_customer_links.append(Customer.gems.through(customer_id=customer.pk, gem_id=gem.pk))
        if customer in top_customers:
            customer.is_in_top_five = True
            customers_to_insert.append(customer)
    Customer.objects.bulk_update(customers_to_insert, fields=('is_in_top_five',))
    Customer.gems.through.objects.bulk_create(gems_to_customer_links)


def mark_gems_to_display():
    """Проверяет все камни(Gem) и изменяет поле is_visible, если этот камень надо отобразить в результатах"""
    gems = Gem.objects.all().prefetch_related('customers')
    gems_to_insert = []
    for gem in gems:
        customer_count = 0
        for customer in gem.customers.all():
            if customer.is_in_top_five:
                customer_count += 1
        if customer_count > 1:
            gem.is_visible = True
            gems_to_insert.append(gem)
    Gem.objects.bulk_update(gems_to_insert, fields=('is_visible',))


def create_customer(operation):
    """
        Создаёт словарь с информацией о покупателе.
        Возвращает созданный словарь
    """
    customer = {
        'username': operation.customer,
        'spent_money': operation.total,
        'gems': {operation.item}
    }
    return customer


def push_customers_to_db(customers_to_insert):
    """
            Сохраняет покупателей(Customer) в БД.
            Возращает созданный Set
        """
    customers_to_insert_list = [{
        'username': customer.get('username'),
        'spent_money': customer.get('spent_money'),
    } for customer in customers_to_insert.values()]

    customers = Customer.objects.bulk_create(Customer(**customer) for customer in customers_to_insert_list)
    return customers


def push_gems_to_db(gems_set):
    """
        Сохраняет камни(Gem) в БД.
        Возращает созданный Set
    """
    gems_to_insert = [{
        'name': gem
    } for gem in gems_set]
    gems = Gem.objects.bulk_create(Gem(**gem) for gem in gems_to_insert)
    return gems


def create_customers_and_gems_from_operations(operations):
    """Создаёт объекты покупателей(Customer) и камней(Gem) на основе операций(Operation)"""
    gems_set = set()
    customers_to_insert = dict()

    for operation in operations:
        gems_set.add(operation.item)
        # Получаем покупателя из списка обработанных ранее. Если он есть - обновляем, иначе - создаём
        customer = customers_to_insert.get(operation.customer)
        if customer:
            customer['spent_money'] = customer['spent_money'] + operation.total
            customer['gems'].add(operation.item)
        else:
            customer = create_customer(operation)
            customers_to_insert[customer['username']] = customer

    customers = push_customers_to_db(customers_to_insert)
    push_gems_to_db(gems_set)

    add_gems_to_customers(customers, customers_to_insert)

    mark_gems_to_display()
