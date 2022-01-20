import const
import io
import typing


class EclatNode:
    """Eclat Node class to support Eclat Tree"""
    def __init__(self, key: float, n_trans: int):
        self.children: typing.List[EclatNode] = list()
        self.key: float = key
        self.transactions = [n_trans]

    @property
    def support(self):
        return len(self.transactions)

    def save_node(
            self,
            level: int = 0,
            parent: "EclatNode" = None,
            out_file=None,
    ):
        """Save the node data on file"""
        out_file.write(f'#L{level} {parent.key if parent.key != 0 else "root"} '
                       f'-> {self.key}, {self.support}, {self.transactions}\n')


class EclatTree:
    """
    Eclat Tree implementation, this class implements all the function
    for create the tree from transactions till the generation of the rules
    """
    def __init__(self, root_t: EclatNode):
        self.root: EclatNode = root_t

    def save_tree(self, dfs: bool = False):
        """Save the tree nodes on file"""
        with open(const.FILENAME_NODES, 'w') as f:
            f.write('#Level parent -> value, support, transactions\n')
            self._save_sub_tree(self.root, self.root, dfs, out_file=f)

    def _save_sub_tree(
            self,
            node: EclatNode,
            parent: EclatNode,
            dfs: bool = False,
            level: int = 0,
            out_file=None,
    ):
        """Recursive function to explore and save the tree nodes"""
        if node:
            if not dfs and node != self.root:
                node.save_node(level, parent, out_file=out_file)
            for child in node.children:
                self._save_sub_tree(child, node, dfs, level + 1,
                                    out_file=out_file)
            if dfs and node != self.root:
                node.save_node(level, parent, out_file=out_file)

    def create_tree_from_transaction(
            self,
            transaction: typing.List[int],
            n_trans: int,
    ):
        """
        Add new nodes and update the existing one from list of items
        in a single transaction
        """
        # Insert root children first
        for element in transaction:
            if self.root.children:
                self._insert_node(self.root, element, n_trans)
            else:
                self.root.children.append(EclatNode(element, n_trans))

        # Add children to root children
        for i in range(len(transaction) - 1):
            for child in self.root.children:
                if child.key == transaction[i]:
                    for j in range(len(transaction[i + 1:])):
                        self._insert_noderen(
                            child, transaction[i + j + 1:], n_trans)

    def _insert_noderen(
            self,
            parent: EclatNode,
            elements: typing.List[int],
            n_trans: int,
    ):
        """Recursive function for inserting elements given the parent"""
        if elements:
            if parent.children:
                self._insert_node(parent, elements[0], n_trans)
            else:
                parent.children.append(EclatNode(elements[0], n_trans))
            if len(elements) > 1:
                for child in parent.children:
                    if child.key == elements[0]:
                        self._insert_noderen(
                            child, elements[1:], n_trans)
                        break

    @staticmethod
    def _insert_node(parent: EclatNode, key: int, n_trans: int):
        """
        Base function for the insertion of a node given the key value,
        its parent and the current transaction number
        """
        for i in range(len(parent.children)):
            # Element equal to the current sibling
            if key == parent.children[i].key:
                parent.children[i].transactions.append(n_trans)
                break

            # Element smaller than the current sibling
            if key < parent.children[i].key:
                if i == 0:
                    new_children = [EclatNode(key, n_trans)]
                    new_children.extend(parent.children)
                    parent.children = new_children
                else:
                    new_children = parent.children[:i]
                    new_children.append(EclatNode(key, n_trans))
                    new_children.extend((parent.children[i:]))
                    parent.children = new_children
                break

            # Element bigger then the bigger sibling
            if len(parent.children) - 1 == i \
                    and key > parent.children[i].key:
                parent.children.append(EclatNode(key, n_trans))
                break

    def count_nodes(self):
        """Count the nodes in the ECLAT tree"""
        nodes = 0
        if self.root.children:
            nodes = self._explore_count_nodes(self.root)
        return nodes

    def _explore_count_nodes(self, node: EclatNode):
        """Recursive function to count the number of nodes in the tree"""
        nodes = 1
        if not node.children:
            return nodes
        for child in node.children:
            nodes += self._explore_count_nodes(child)
        return nodes

    def find_max_support(self):
        """Find the node with the maximum support"""
        max_sup = 0
        if self.root.children:
            max_sup = max(
                max([child.support for child in self.root.children]), max_sup)
        return max_sup

    def remove_nodes_by_support(self, support: int):
        """Interface for removing nodes with support < threshold support"""
        self._remove_nodes_by_support(self.root, support)

    def _remove_nodes_by_support(self, parent: EclatNode, support: int):
        """
        Recursive function for removing nodes with support < threshold support
        """
        parent.children = [
            child for child in parent.children if not child.support < support]
        for child in parent.children:
            self._remove_nodes_by_support(child, support)

    def generate_association_rules(
            self,
            min_support: float = 0,
            min_confidence: float = 0,
            num_antecedents: int = 1,
    ):
        """
        Generation for association rules that follows the constraints
            min_support -- Minimum support threshold
            min_confidence -- Minimum confidence threshold
            num_antecedents -- Exact number of antecedent in the rule
        """
        rules = []
        for child in self.root.children:
            gen_rules = self._generate_rules_from_parent(child, num_antecedents)
            for r in gen_rules:
                # To avoid having the antecedent in the consequent
                if r.get('consequents'):
                    confidence = (r.get('support_c') / r.get('support_a')) \
                        if r.get('support_a') else 0
                    if (min_confidence and confidence >= min_confidence
                        or not min_confidence) and \
                            (min_support and
                             r.get('support_c') >= min_support
                             or not min_support):
                        rules.append({
                            'antecedents': r.get('antecedents'),
                            'consequents': r.get('consequents'),
                            'support': r.get('support_c'),
                            'confidence': float("{:.3f}".format(confidence)),
                        })
        return rules

    def _generate_rules_from_parent(
            self, parent, num_antecedents: int = 1):
        """
        Recursive function for generate association rules given the parent node
        and the number of antecedent that the rules has to have
        """
        if parent.children:
            rules = list()
            for child in parent.children:
                antecedents = list()
                consequents = list()
                if num_antecedents < 1:
                    consequents = [parent.key]
                else:
                    antecedents = [parent.key]
                new_rules = self._generate_rules_from_parent(
                    child, num_antecedents=(num_antecedents - 1))
                if new_rules:
                    support_c = 0
                    support_a = parent.support if num_antecedents == 1 else 0
                    for r in new_rules:
                        antecedents.extend(r.get('antecedents'))
                        consequents.extend(r.get('consequents'))
                        support_a = r.get('support_a') \
                            if r.get('support_a') != 0 else support_a
                        support_c = r.get('support_c')
                    rules.append({
                        'antecedents': antecedents,
                        'consequents': consequents,
                        'support_a': support_a,
                        'support_c': support_c,
                    })
            return rules
        else:
            if num_antecedents < 1:
                return [{
                    'antecedents': list(),
                    'consequents': [parent.key],
                    'support_a': 0,
                    'support_c': parent.support,
                }]
            else:
                return [{
                    'antecedents': [parent.key],
                    'consequents': list(),
                    'support_a': parent.support,
                    'support_c': 0,
                }]
