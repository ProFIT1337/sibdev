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


def parse_file(reader):
    """
        Парсит файл, создавая списки из объектов операций(Operation), покупателей(Customer) и камней(Gem).
        Возращает полученные списки
    """
    operations_to_insert = []
    gems_set = set()
    customers_to_insert = dict()

    for row in reader:
        operation = create_operation(row)
        operations_to_insert.append(operation)

        gems_set.add(operation.get('item'))

        # Получаем покупателя из списка обработанных ранее. Если он есть - обновляем, иначе - создаём
        customer = customers_to_insert.get(operation.get('customer'))
        if customer:
            customer['spent_money'] = customer['spent_money'] + operation.get('total')
            customer['gems'].add(operation.get('item'))
        else:
            customer = create_customer(operation)
            customers_to_insert[customer['username']] = customer

    return customers_to_insert, gems_set, operations_to_insert


def add_gems_to_customers(customers, customers_dict):
    """Добавляет купленные пользователями камни в поле gems модели Customer"""
    gems = Gem.objects.all()
    top_customers = get_top_customers(customers)
    customers_to_insert = []
    gems_to_customer_links = []
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


def create_operation(row):
    """
        Создаёт словарь с информацией об операции.
        Возвращает созданный словарь
    """
    operation = {
        'customer': row[0],
        'item': row[1],
        'total': int(row[2]),
        'quantity': int(row[3]),
        'date': row[4]
    }
    return operation


def create_customer(operation):
    """
        Создаёт словарь с информацией о покупателе.
        Возвращает созданный словарь
    """
    customer = {
        'username': operation.get('customer'),
        'spent_money': operation.get('total'),
        'gems': {operation.get('item')}
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


def push_data_to_db(customers_to_insert, gems_set, operations_to_insert):
    """
        Сохраняет операции(Operation), покупателей(Customer) и камни(Gem) в БД.
        Возвращает кортеж из полученных наборов данных
    """
    customers = push_customers_to_db(customers_to_insert)
    gems = push_gems_to_db(gems_set)
    add_gems_to_customers(customers, customers_to_insert)
    mark_gems_to_display()
    operations = Operation.objects.bulk_create(Operation(**operation) for operation in operations_to_insert)
    return customers, gems, operations
