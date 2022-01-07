import datetime
from eclat_tree import EclatTree, EclatNode

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
    print('Removing the nodes with support < ' + str(support) + ' ...')
    eclat_tree.remove_children_by_support(support)
    print('Number of nodes: ' + str(eclat_tree.count_rules()))
    eclat_tree.print_tree()

