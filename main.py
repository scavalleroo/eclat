import const
import datetime
import sys
import typing
from eclat_tree import EclatTree, EclatNode


def save_rules(rules_t: typing.List[typing.Dict]):
    """
    Save rules on file the filename is set in const.FILENAME_RULES
    save_rules(rules_t: typing.List[typing.Dict]):

    Keyword arguments:
    rules_t -- list of rules to save on file
    """
    with open(const.FILENAME_RULES, 'w') as f:
        if rules_t:
            s = ", "
            count = 1
            f.write('#n° ant. => consequents [support, confidence]\n')
            for r in rules_t:
                f.write(f"#{count} "
                        f"{s.join(str(item) for item in r.get('antecedents'))}"
                        f" => "
                        f"{s.join(str(item) for item in r.get('consequents'))} "
                        f"[{r.get('support')}, {r.get('confidence')}]\n")
                count += 1
        else:
            f.write('No rules found')
        f.close()


def save_rules_with_all_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    """
    Save rules that have all the elements in the list items_set
    save_rules_with_all_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
    ):

    Keyword arguments:
    rules_t -- list of rules to to check and save
    items_set -- list of items to check inside the rule
    """
    new_rules = list()
    for r in rules_t:
        if all(item in r.get('antecedents') or item in r.get('consequents')
               for item in items_set):
            new_rules.append(r)
    save_rules(new_rules)
    print(f'Number of matched rules {len(new_rules)}')


def save_rules_with_some_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    """
    Save rules that have some of the elements in the list items_set
    save_rules_with_some_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
    ):

    Keyword arguments:
    rules_t -- list of rules to to check and save
    items_set -- list of items to check inside the rule
    """
    new_rules = list()
    for r in rules_t:
        if any(item in r.get('antecedents') or item in r.get('consequents')
               for item in items_set):
            new_rules.append(r)
    save_rules(new_rules)
    print(f'Number of matched rules {len(new_rules)}')


def save_rules_with_none_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
):
    """
    Save rules that have none of the elements in the list items_set
    save_rules_with_all_elements_in_set(
        rules_t: typing.List[typing.Dict],
        items_set: typing.List[int] = None,
    ):

    Keyword arguments:
    rules_t -- list of rules to to check and save
    items_set -- list of items to check inside the rule
    """
    new_rules = list()
    for r in rules_t:
        if not any(item in r.get('antecedents') or item in r.get('consequents')
                   for item in items_set):
            new_rules.append(r)
    save_rules(new_rules)
    print(f'Number of matched rules {len(new_rules)}')


def discretize_data(
        transactions: typing.List[typing.List],
        n_classes: int = None,
) -> typing.List[typing.List]:
    """
    Discretize the attributes in the transactions in more discrate values based
    on the number of classes.
    discretize_data(
        transactions: typing.List[typing.List],
        n_classes: int = None,
    ) -> typing.List[typing.List]:

    Keyword arguments:
    transactions -- list of transactions where each item is a set of items in
    the transaction
    n_classes -- number of subrange to generate for each attribute, the size of
    the range is computed taking the maximum gap and dividing it by the
    number of classes
    """
    if transactions:
        maxes = [0] * len(transactions[0])
        mins = [200] * len(transactions[0])
        for transaction in transactions:
            i = 0
            for value in transaction:
                if maxes[i] < value:
                    maxes[i] = value
                elif mins[i] > value:
                    mins[i] = value
                i += 1
        ranges = [[]] * len(maxes)
        for i in range(len(maxes)):
            step = (maxes[i] - mins[i]) / n_classes
            for j in range(n_classes):
                ranges[i].append(mins[i] + step * j)

        for transaction in transactions:
            i = 0
            for value in transaction:
                value = float(value)
                for j in range(len(ranges[i])):
                    if ranges[i][j] > value:
                        transaction[i] = ranges[i][j - 1]
                        break
                i += 1
        return transactions


def main():
    """
    Main function, the operation performed are:
     - Reading the configuration file
     - Reading the transactions
     - Discretization if it is set
     - Bulding ECLAT tree
     - Remove nodes from the tree with support < threshold support
     - Saving ECLAT nodes
     - Generate association rules
     - Filter the association rules
     - Save the association rules
    """
    # Configuration file
    with open("data.conf", "r") as f:
        temp = f.read().splitlines()
        # Name of the dataset file (string).
        filename = temp[0]
        print(f'Dataset [{filename}]')
        # Minimum support threshold for each node (integer number).
        support_node = int(temp[1])
        print(f'Support of nodes [{support_node}]')
        # Minimum support threshold for each association rule (integer number).
        support_rule = int(temp[2])
        print(f'Support of rules [{support_rule}]')
        # Minimum confidence threshold for each association rule (float number).
        confidence = float(temp[3])
        print(f'Min confidence [{confidence}]')
        # Type of constraint to apply to the generated rules (‘some’ for c_1,
        # ‘all’ for c_2, ‘none’ for c_3, ‘’ for no constraint).
        filter = temp[4]
        print(f'Type of filter [{filter}]')
        # List of the item IDs that have to match the chosen constraint in
        # the preview line (list of integers).
        filter_list = temp[5].split(' ')
        if '\n' in filter_list:
            filter_list.remove('\n')
        filter_list = [float(item) for item in filter_list]
        print(f'Filter list {filter_list}')
        print()
        # Number of antecedent in the generated rule
        num_antecedents = int(temp[6])
        print(f'Number of antecedents in association rules [{num_antecedents}]')
        discretization = bool(int(temp[7]))
        print(discretization)
        print(f'Is discretization performed? '
              f'{"Yes" if discretization else "No"}')
        # Number of classes used for discatization
        if discretization:
            num_classes = int(temp[8])
            print(f'Number of classes used for dataset discretization '
                  f'[{num_classes}]')
        f.close()

    # Reading the dataset file and generating the list of transactions
    transactions = list()
    with open(filename, "r") as f:
        items = 0
        for x in f:
            transaction = x.split(' ')
            if '\n' in transaction:
                transaction.remove('\n')
            transactions.append([float(item) for item in transaction])
            items += len(transaction)
        f.close()

    if discretization:
        transactions = discretize_data(transactions, num_classes)

    print(f'Number of transaction {len(transactions)}')
    print(f'Average number of items in transactions {items/len(transactions)}')
    print()

    print('Building the tree...')
    print(f'[{datetime.datetime.now()}] Execution started.')
    print('This process can take a few minutes...')
    eclat_tree = EclatTree(root_t=EclatNode(0, 0))
    for i in range(len(transactions)):
        eclat_tree.create_tree_from_transaction(transactions[i], i + 1)
    print('Generation of the tree completed')
    print(f'[{datetime.datetime.now()}] Execution completed.')
    print()

    print(f'Number of nodes in the ECALT tree {eclat_tree.count_nodes()}')
    print(f'Max support in nodes {eclat_tree.find_max_support()}')
    print()

    print(f'Removing the nodes with support < {str(support_node)}')
    eclat_tree.remove_nodes_by_support(support_node)
    print(f'Number of nodes in the ECALT tree {eclat_tree.count_nodes()}')
    eclat_tree.save_tree()
    print()

    print(f'[{datetime.datetime.now()}] Generating association rules with '
          f'support >= {support_rule} confidence >= {confidence}')
    rules = eclat_tree.generate_association_rules(
        min_support=support_rule,
        min_confidence=confidence,
        num_antecedents=num_antecedents,
    )
    print(f'[{datetime.datetime.now()}] Generation of the rules completed')
    print(f'Total number of rules {len(rules)}')
    print()

    print(f'Saving rules with {filter} elements in {filter_list}')
    if filter == 'some':
        save_rules_with_some_elements_in_set(rules, filter_list)
    elif filter == 'all':
        save_rules_with_all_elements_in_set(rules, filter_list)
    elif filter == 'none':
        save_rules_with_none_elements_in_set(rules, filter_list)
    else:
        save_rules(rules)
    print(f'Check the file {const.FILENAME_RULES}')


if __name__ == '__main__':
    main()
