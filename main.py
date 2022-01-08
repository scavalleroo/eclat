import datetime
import typing

from eclat_tree import EclatTree, EclatNode


def print_rules(rules_t: typing.List[typing.Dict]):
    if rules_t:
        for r in rules_t:
            print(r)
    else:
        print('No rules found')


def print_rules_with_all_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    new_rules = list()
    for r in rules_t:
        if all(item in r.get('antecedent')
               or item in r.get('consequent').get('elements')
               for item in items_set):
            new_rules.append(r)
    print_rules(new_rules)


def print_rules_with_some_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    new_rules = list()
    for r in rules_t:
        if any(item in r.get('antecedent')
               or item in r.get('consequent').get('elements')
               for item in items_set):
            new_rules.append(r)
    print_rules(new_rules)


def print_rules_with_none_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    new_rules = list()
    for r in rules_t:
        if not any(item in r.get('antecedent')
                   or item in r.get('consequent').get('elements')
                   for item in items_set):
            new_rules.append(r)
    print_rules(new_rules)


if __name__ == '__main__':
    print('This process can take a few minutes...')
    print(f'[{datetime.datetime.now()}] Execution started.')
    print('Building the tree...')
    eclat_tree = EclatTree(root_t=EclatNode(0, 0))
    transactions = list()
    f = open("data_custom.dat", "r")

    for x in f:
        transaction = x.split(' ')
        if '\n' in transaction:
            transaction.remove('\n')
        transactions.append([int(item) for item in transaction])
    f.close()

    for i in range(len(transactions)):
        eclat_tree.create_tree_from_transaction(transactions[i], i + 1)
    print(f'[{datetime.datetime.now()}] Execution completed.')

    # Configuration file
    f = open("data.conf", "r")
    # First line is support
    support = int(f.readline())
    f.close()

    print('Number of nodes: ' + str(eclat_tree.count_rules()))
    print('Max support: ' + str(eclat_tree.find_max_support()))
    # print('Removing the nodes with support < ' + str(support) + ' ...')
    # eclat_tree.remove_children_by_support(support)
    # print('Number of nodes: ' + str(eclat_tree.count_rules()))
    eclat_tree.print_tree()
    rules = eclat_tree.generate_association_rules()
    print_rules_with_none_elements_in_set(rules, [1, 2])
