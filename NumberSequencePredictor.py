import random

class NumberSequencePredictor:
    """
    A class that predicts the continuation of numeric sequences based on mathematical expressions.

    This class generates random expressions composed of basic mathematical operations (+, -, *) 
    and tries to match them to a given sequence. Once a match is found, the class can predict 
    the next values in the sequence.

    Attributes:
        function_symbols (list): List of function symbols used in the expressions (default: ['+', '-', '*']).
        constant_leaves (list): List of constant values used as leaves in the expressions (default: range(-2, 3)).
        variable_leaves (list): List of variable symbols used in the expressions (default: ['x', 'y', 'i']).
        leaves (list): Combined list of constant and variable leaves.
        max_depth (int): Maximum depth for the random expression tree (default: 3).

    Methods:
        __init__(self, function_symbols=None, constant_leaves=None, variable_leaves=None, max_depth=3):
            Initializes the predictor with custom or default values for function symbols, leaves, and max depth.

        predict_rest(sequence):
            Predicts the next values in a given sequence based on a generated expression.
    """

    
    def __init__(self, function_symbols=None, constant_leaves=None, variable_leaves=None, max_depth=3):
        """
        Initializes the NumberSequencePredictor with the given function symbols, constant leaves, and max depth.

        Parameters:
            function_symbols (list): The list of function symbols to be used in expressions (e.g., ['+', '-', '*']).
            constant_leaves (list): The list of constant values to be used as leaves in expressions.
            variable_leaves (list): The list of variable names to be used as leaves in expressions.
            max_depth (int): The maximum depth of generated expressions.

        Returns:
            None
        """
        self.function_symbols = function_symbols or ['+', '-', '*']
        self.constant_leaves = constant_leaves or list(range(-2, 3))
        self.variable_leaves = variable_leaves or ['x', 'y', 'i']
        self.leaves = self.constant_leaves + self.variable_leaves
        self.max_depth = max_depth
    
    def _depth(self, expression, recursion_depth=0):
        """Private method: Takes an expression and returns depth of the expression tree."""
        if type(expression) in [int, str]:
            return recursion_depth
        else:
            dpth = max(self._depth(e, recursion_depth + 1) for e in expression)
            return dpth

    def _is_valid_expression(self, obj, recursion_depth=0):
        """Private method: Tests whether an object is a valid expression."""
        if type(obj) in [int, str]:
            if obj in self.leaves or (obj in self.function_symbols and recursion_depth != 0) or type(obj) == int:
                return True
        elif type(obj) == list and len(obj) == 3:
            if type(obj[0]) == str and obj[0] in self.function_symbols:
                valid = all(self._is_valid_expression(o, recursion_depth + 1) for o in obj)
                return valid
        return False

    def _random_expression(self, current_depth=0):
        """Private method: Generates a random expression given the function symbols, leaves, and max depth."""
        if current_depth == self.max_depth:
            return random.choice(self.leaves)
        else: 
            p = random.random()
            leaf = False
            if p > 0.5:
                leaf = True
            if leaf:
                return random.choice(self.leaves)
            else:
                choice = [random.choice(self.function_symbols), 
                          self._random_expression(current_depth + 1),
                          self._random_expression(current_depth + 1)]
            return choice 

    def _prune(self, expression, max_depth, current_depth=0):
        """Private method: Prunes the expression to fit within the max depth."""
        if type(expression) in [int, str]:
            return expression
        if current_depth == max_depth:
            return random.choice(self.leaves)
        if type(expression) == list and len(expression) == 3:
            return [expression[0], 
                    self._prune(expression[1], max_depth, current_depth + 1), 
                    self._prune(expression[2], max_depth, current_depth + 1)]

    def _count_nodes(self, expr):
        """Private method: Counts the number of nodes in an expression tree."""
        if type(expr) in [int, str]:
            return 1
        elif type(expr) == list and len(expr) == 3:
            return 1 + self._count_nodes(expr[1]) + self._count_nodes(expr[2])

    def _attach(self, expression1, expression2, position, current_pos=0):
        """Private method: Attaches expression2 into expression1 at the given preorder position."""
        if position == current_pos:
            return expression2
        if type(expression1) in [int, str]:
            return expression1  
        if type(expression1) == list and len(expression1) == 3:
            root = expression1[0]
            lp = current_pos + 1
            left = self._attach(expression1[1], expression2, position, lp)
            left_node_count = self._count_nodes(expression1[1])
            rp = lp + left_node_count
            right = self._attach(expression1[2], expression2, position, rp)
            return [root, left, right]

    def _evaluate(self, expression, bindings):
        """Private method: Evaluates an expression given a dictionary of bindings."""
        if type(expression) == int:
            return expression
        elif type(expression) == str:
            return bindings.get(expression)
        else:
            operator = bindings.get(expression[0])
            val_1, val_2 = self._evaluate(expression[1], bindings), self._evaluate(expression[2], bindings)
            return operator(val_1, val_2)

    def _generate_rest(self, initial_sequence, expression, length):
        """Private method: Generates a sequence given the initial sequence, expression, and length."""
        index = len(initial_sequence)
        result = initial_sequence[::]
        for i in range(len(initial_sequence), len(initial_sequence) + length):
            x = result[i - 2]
            y = result[i - 1]
            bindings = {'x': x, 'y': y, 'i': i, 
                        '+': lambda x, y: x + y, 
                        '*': lambda x, y: x * y,
                        '-': lambda x, y: x - y}
            result.append(self._evaluate(expression, bindings))
        return result[index:]

    def predict_rest(self, sequence):
        """
        Predicts the next values in a given sequence based on a generated expression.

        Parameters:
            sequence (list): A list of numbers representing the initial sequence.

        Returns:
            list: A list containing the predicted next values in the sequence.
        """

        ex_sequence = []
        while True:
            ex_sequence = []
            expr = self._random_expression()
            if self._is_valid_expression(expr):
                for i in range(len(sequence)):
                    x = sequence[i - 2] if i > 1 else sequence[0]
                    y = sequence[i - 1] if i > 0 else sequence[1]
                    bindings = {'x': x, 'y': y, 'i': i, 
                                '+': lambda x, y: x + y, 
                                '*': lambda x, y: x * y,
                                '-': lambda x, y: x - y}
                    ex_sequence.append(self._evaluate(expr, bindings))
                if ex_sequence[2:] == sequence[2:]:
                    break
        return self._generate_rest(sequence, expr, 5)

