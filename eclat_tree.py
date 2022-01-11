import typing


class EclatNode:
    def __init__(self, data: int, n_trans: int):
        self.children: typing.List[EclatNode] = list()
        self.key: int = data
        self.transactions = [n_trans]

    @property
    def support(self):
        return len(self.transactions)

    def print_node(self, level: int = 0, parent: "EclatNode" = None):
        print('#' + str(level) + ' ' + str(parent.key) + ' -> ' +
              str(self.key) + ', sup: ' + str(self.support) + ' ', end='')
        print(self.transactions)


class EclatTree:
    def __init__(self, root_t: EclatNode):
        self.root: EclatNode = root_t

    def print_tree(self, dfs: bool = False):
        self._print_sub_tree(self.root, self.root, dfs)

    def _print_sub_tree(
            self,
            node: EclatNode,
            parent: EclatNode,
            dfs: bool = False,
            level: int = 0,
    ):
        if node:
            if not dfs and node != self.root:
                node.print_node(level, parent)
            for child in node.children:
                self._print_sub_tree(child, node, dfs, level + 1)
            if dfs and node != self.root:
                node.print_node(level, parent)

    def create_tree_from_transaction(
            self,
            transaction: typing.List[int],
            n_trans: int,
    ):
        # Insert root children first
        for element in transaction:
            if self.root.children:
                self._insert_child(self.root, element, n_trans)
            else:
                self.root.children.append(EclatNode(element, n_trans))

        # Add children to root children
        for i in range(len(transaction)-1):
            for child in self.root.children:
                if child.key == transaction[i]:
                    self.insert_children(child, transaction[i + 1:], n_trans)

    def insert_children(
            self,
            parent: EclatNode,
            elements: typing.List[int],
            n_trans: int,
    ):
        if elements:
            for i in range(len(elements)):
                if parent.children:
                    self._insert_child(parent, elements[i], n_trans)
                else:
                    parent.children.append(EclatNode(elements[i], n_trans))
                if len(elements) > 1:
                    for child in parent.children:
                        if child.key == elements[i]:
                            self.insert_children(child, elements[i+1:], n_trans)

    @staticmethod
    def _insert_child(parent: EclatNode, element: int, n_trans: int):
        for i in range(len(parent.children)):
            # Element equal to the current sibling
            if element == parent.children[i].key:
                parent.children[i].transactions.append(n_trans)
                break

            # Element smaller than the current sibling
            if element < parent.children[i].key:
                if i == 0:
                    new_children = [EclatNode(element, n_trans)]
                    new_children.extend(parent.children)
                    parent.children = new_children
                else:
                    new_children = parent.children[:i]
                    new_children.append(EclatNode(element, n_trans))
                    new_children.extend((parent.children[i:]))
                    parent.children = new_children
                break

            # Element bigger then the bigger sibling
            if len(parent.children) - 1 == i \
                    and element > parent.children[i].key:
                parent.children.append(EclatNode(element, n_trans))
                break

    def count_nodes(self):
        rules = 0
        if self.root.children:
            rules = self._explore_count_rules(self.root)
        return rules

    def _explore_count_rules(self, node: EclatNode):
        count = 1
        if not node.children:
            return count
        for child in node.children:
            count += self._explore_count_rules(child)
        return count

    def find_max_support(self):
        max_sup = 0
        node = None
        if self.root.children:
            max_sup = max(
                max([child.support for child in self.root.children]), max_sup)
        return max_sup

    def remove_children_by_support(self, support: int):
        self._remove_children_by_support(self.root, support)

    def _remove_children_by_support(self, parent: EclatNode, support: int):
        parent.children = [
            child for child in parent.children if not child.support < support]
        for child in parent.children:
            self._remove_children_by_support(child, support)

    def generate_association_rules(self, min_confidence: float = None):
        rules = []
        for child in self.root.children:
            new_rules = self.generate_rules_from_parent(child)
            for consequent in new_rules:
                consequent.get('elements').pop(0)
                if consequent.get('elements'):
                    confidence = consequent.get('support') / child.support
                    if min_confidence and confidence >= min_confidence \
                            or not min_confidence:
                        rules.append({
                            'antecedent': [child.key],
                            'consequent': consequent,
                            'confidence': confidence,
                        })
        return rules

    def generate_rules_from_parent(self, parent):
        if parent.children:
            rules = []
            for child in parent.children:
                rule = [parent.key]
                new_rules = self.generate_rules_from_parent(child)
                if new_rules:
                    support = 0
                    for r in new_rules:
                        rule.extend(r.get('elements'))
                        support = r.get('support')
                    rules.append({'elements': rule, 'support': support})
            return rules
        else:
            return [{'elements': [parent.key], 'support': parent.support}]
