from itertools import combinations


class Node:
    def __init__(self, state, active, recent=None):
        self.state = state
        self.active = active
        self.mostRecentOperator = recent

    def __str__(self):
        return (f"\nstate: {self.state}\n"
                f"active: {self.active}\n"
                f"mostRecentOperator: {self.mostRecentOperator}")


def add_operator(state, operator, indexes):
    flag = False
    next_state = []
    if state:
        for i in range(len(state)):
            if indexes[state[i]] >= indexes[operator]:
                next_state = state[0:i] + [operator] + state[i:]
                flag = True
                break
        if not flag:
            next_state = state.copy()
            next_state.append(operator)
    else:
        next_state = [operator]
    return next_state


def generate_child(node, operator, indexes):
    child_active = node.active.copy()
    child_active.remove(operator)
    child_state = add_operator(node.state, operator, indexes)
    return Node(child_state, child_active, operator)


def check(new_nodes, remaining_operators, goal_state, indexes):
    changed_nodes = new_nodes.copy()
    changed_remaining_operators = remaining_operators.copy()
    for node in new_nodes:
        flag = False
        if len(node.state) < len(goal_state):
            for operator in remaining_operators:
                flag = False
                next_state = add_operator(node.state, operator, indexes)
                for i in range(len(next_state)):
                    if (next_state[i] not in goal_state or
                            next_state.count(next_state[i] != goal_state.count(next_state[i]))):
                        flag = True
                        break
                if not flag:
                    break
        if flag:
            del changed_remaining_operators[changed_remaining_operators.index(node.mostRecentOperator)]
            changed_nodes.discard(node)
    return changed_nodes, changed_remaining_operators


def opus_s(operators, goal_state):
    open_list = [Node([], operators)]
    indexes = {operators[i]: i for i in range(len(operators))}
    while open_list:
        cur_node = open_list[0]
        del open_list[0]
        remaining_operators = cur_node.active
        new_nodes = set()
        for operator in cur_node.active:
            child = generate_child(cur_node, operator, indexes)
            if child.state == goal_state:
                return child
            new_nodes.add(child)
        new_nodes, remaining_operators = check(new_nodes, remaining_operators, goal_state, indexes)
        changed_nodes = new_nodes.copy()
        for node in new_nodes:
            changed_nodes.discard(node)
            node.active = remaining_operators.copy()
            if node.mostRecentOperator in node.active:
                del node.active[node.active.index(node.mostRecentOperator)]
            changed_nodes.add(node)
        new_nodes = changed_nodes
        for node in new_nodes:
            open_list.append(node)
    return False


def _value(node, goal_state):
    if node.state == goal_state:
        return float("inf")
    else:
        val = 0
        if len(node.state) > len(goal_state):
            return float("-inf")
        for i in range(len(node.state)):
            if node.state[i] == goal_state[i]:
                val += 1
        return val


def _optimistic_value(node, operators, goal_state, value=_value):
    best_value = float("-inf")
    for i in range(1, len(operators) + 1):
        for el in list(combinations(operators, i)):
            if not node.state:
                # next_state = delimiter.join(*el)
                next_state = [el[i] for i in range(len(el))]
            else:
                # next_state = delimiter.join([node.state, *el])
                next_state = node.state.copy()
                for j in range(len(el)):
                    next_state.append(el[j])
            val = value(Node(next_state, operators), goal_state)
            if val == float("inf"):
                return val
            if val > best_value:
                best_value = val
    return best_value


def opus_o(operators, goal_state, value=_value, optimistic_value=_optimistic_value):
    open_list = [Node([], operators)]
    best = open_list[0]
    indexes = {operators[i]: i for i in range(len(operators))}
    while open_list:
        cur_node = open_list[0]
        del open_list[0]
        remaining_operators = cur_node.active
        new_nodes = set()
        for operator in cur_node.active:
            child = generate_child(cur_node, operator, indexes)
            if child.state == goal_state:
                return child
            if value(child, goal_state) > value(best, goal_state):
                best = child
                for i in range(len(open_list) - 1, -1, -1):
                    if (optimistic_value(open_list[i], open_list[i].active, goal_state, value=value)
                            < value(best, goal_state)):
                        del open_list[i]
            new_nodes.add(child)
        new_nodes, remaining_operators = check(new_nodes, remaining_operators, goal_state, indexes)
        # сортировка new_nodes по уменьшению optimistic_value(n, remaining_operators)
        changed_nodes = new_nodes.copy()
        for node in new_nodes:
            changed_nodes.discard(node)
            node.active = remaining_operators.copy()
            if node.mostRecentOperator in node.active:
                del node.active[node.active.index(node.mostRecentOperator)]
            changed_nodes.add(node)
        new_nodes = changed_nodes
        for node in new_nodes:
            if (optimistic_value(node, node.active, goal_state, value=value) >
                    value(best, goal_state)):
                open_list.append(node)
    return best
