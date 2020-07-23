# Here are a few functions to feed, query and represent the suffix tree generated
# by the online generalized ST algorithm implemented in TreeBuilder.


from TreeBuilder import OnlineGeneralizedSuffixTree


class SuffixTree(OnlineGeneralizedSuffixTree):
    """A class to implement ways to interact with the tree built by OnlineGeneralizedSuffixTree.
    ...
    Methods
    -------
    add_sequence(sequence, sequence_index)
        Append 'sequence' to the string 'self.sequences[sequence_index]'
        (prepare the tree to receive a new sequence if 'sequence_index' is not a key
        in the dictionary 'self.sequences'), and update the tree one character/token at a time.
        Note that 'sequence' can be a string or a list of tokens (alarms, events...).
    draw_tree(node, repr_edge, last)
        Print the tree rooted at node 'node' ('repr_edge' and 'last' used for recursion).
    is_pattern_present(pattern, node)
        Check if the pattern 'pattern' is present in the tree rooted at node 'node'.
    find_patterns_appear_more_than_n_times(n_times, node)
        Find the patterns that appear more than 'n_times' times in the tree rooted at node 'node'.
    find_patterns_longer_than_length_appear_more_than_n_times(length, n_times, node)
        Find the patterns of length at least 'length' that appear more than
        'n_times' times  in the tree rooted at node 'node'.
    """

    def add_sequence(self, sequence, sequence_index='sequence0'):
        """Append 'sequence' to the string 'self.sequences[sequence_index]'
        (prepare the tree to receive a new sequence if 'sequence_index' is not a key
        in the dictionary 'self.sequences'), and update the tree one character/token at a time.
        Note that 'sequence' can be a string or a list of tokens (alarms, events...).
        sequence: str (or list[tokens])
        sequence_index: str
        """
        self.active_sequence = sequence_index
        if sequence_index not in self.sequences:
            self.sequences[sequence_index] = []
            active_point = self.ActivePoint(active_node=self.root)
            self.active_points[sequence_index] = active_point
        for letter in sequence:
            self.sequences[self.active_sequence].append(letter)
            self.created_nodes_during_step = []
            self.active_points[self.active_sequence].remainder += 1
            self.insert_suffix()

    def draw_tree(self, node=None, repr_edge='|', last=False):
        """ Print the tree rooted at node 'node'. 'repr_edge' and 'last' used for recursion.
        node: Node
        repr_edge: str
        last: bool
        """
        if node is None:
            node = self.root
            print(self.sequences)
        else:
            if node.incoming_edge.canonical_range[1] == -1:
                # Normal Mode:
                print(f"{repr_edge}_{self.sequences[node.incoming_edge.canonical_sequence][node.incoming_edge.canonical_range[0]:len(self.sequences[node.incoming_edge.canonical_sequence])]} at positions: {node.starting_positions}")  # Normal Mode
                # Debug Mode:
                # print(f"{repr_edge}_{self.sequences[node.incoming_edge.canonical_sequence][node.incoming_edge.canonical_range[0]:len(self.sequences[node.incoming_edge.canonical_sequence])]} at positions: {node.starting_positions} edge {node.incoming_edge} node {node}, depth: {node.depth} {'<--- Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge' if node.incoming_edge==self.active_points[self.active_sequence].active_edge else ''}")  # Debug Mode
            else:
                # Normal Mode:
                print(f"{repr_edge}_{self.sequences[node.incoming_edge.canonical_sequence][node.incoming_edge.canonical_range[0]:node.incoming_edge.canonical_range[1]]} at positions: {node.starting_positions}")  # Normal Mode
                # Debug Mode:
                # print(f"{repr_edge}_{self.sequences[node.incoming_edge.canonical_sequence][node.incoming_edge.canonical_range[0]:node.incoming_edge.canonical_range[1]]} at positions: {node.starting_positions} edge {node.incoming_edge} node {node}, depth: {node.depth} {'<--- Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge Incoming edge is active edge' if node.incoming_edge==self.active_points[self.active_sequence].active_edge else ''}")  # Debug Mode
            if last:
                repr_edge = repr_edge[0:-2]
                repr_edge += ' '*5*self.length(node.incoming_edge)
                repr_edge += '  |'
            else:
                repr_edge += ' ' * 5 * self.length(node.incoming_edge)
                repr_edge += '|'
        for edge in node.edges:
            self.draw_tree(edge.node_to, repr_edge, edge == node.edges[-1])

    def is_pattern_present(self, pattern, node=None):
        """Check if the pattern 'pattern' is present in the subtree rooted at 'node'.
        If 'node' is not specified, check for the entire tree.
        pattern: str
        node: Node
        """
        if node is None:
            node = self.root
            print(f'\nThe pattern \"{pattern}\"', end='')
        for edge in node.edges:
            if pattern[0:min(len(pattern), self.length(edge))] == ''.join(self.sequences[edge.canonical_sequence][edge.canonical_range[0]: min(edge.canonical_range[0] + len(pattern), edge.canonical_range[1])]):
                if self.length(edge) < len(pattern):
                    return self.is_pattern_present(pattern=pattern[self.length(edge):], node=edge.node_to)
                else:
                    print(f' is present in "sequences" and appears at positions {edge.node_to.starting_positions}.')
                    return
        print(' is not present in "sequences".')

    def find_patterns_appear_more_than_n_times(self, n_times, node=None):
        """ Find the patterns that appear more than 'n_times' times in the subtree rooted
        at node 'node'. If 'node' is not specified, check for the entire tree.
        n_times: int
        node: Node
        """
        if node is None:
            print(f'\nPatterns that appear more than {n_times} times:')
            node = self.root
        for edge in node.edges:
            node_occurrences = 0
            for sequence_index in edge.node_to.starting_positions:
                node_occurrences += len(edge.node_to.starting_positions[sequence_index])
            if node_occurrences >= n_times:
                if edge.node_to.depth == -1:
                    print(
                        f'    The pattern \"{"".join(self.sequences[edge.canonical_sequence][len(self.sequences[edge.canonical_sequence]) - edge.node_to.depth: len(self.sequences[edge.canonical_sequence])])}\" appears {node_occurrences} times at positions: {edge.node_to.starting_positions}.')
                else:
                    print(
                        f'    The pattern \"{"".join(self.sequences[edge.canonical_sequence][edge.canonical_range[1] - edge.node_to.depth: edge.canonical_range[1]])}\" appears {node_occurrences} times at positions: {edge.node_to.starting_positions}.')
                    self.find_patterns_appear_more_than_n_times(n_times, edge.node_to)

    def find_patterns_longer_than_length_appear_more_than_n_times(self, length, n_times, node=None):
        """ Find the patterns of length at least 'length' that appear more than 'n_times'
        times  in the subtree rooted at node 'node'. If 'node' is not specified, check for the entire tree.
        length: int
        n_times: int
        node: Node
        """
        if node is None:
            print(f'\nPatterns longer than {length} that appear more than {n_times} times:')
            node = self.root
        for edge in node.edges:
            node_occurrences = 0
            for sequence_index in edge.node_to.starting_positions:
                node_occurrences += len(edge.node_to.starting_positions[sequence_index])
            if node_occurrences >= n_times:
                if edge.node_to.depth == -1:
                    if len(self.sequences[edge.canonical_sequence]) >= length:
                        print(f'    The pattern \"{"".join(self.sequences[edge.canonical_sequence][len(self.sequences[edge.canonical_sequence]) - edge.node_to.depth: len(self.sequences[edge.canonical_sequence])])}\" appears {node_occurrences} times at positions: {edge.node_to.starting_positions}.')
                else:
                    if edge.node_to.depth >= length:
                        print(f'    The pattern \"{"".join(self.sequences[edge.canonical_sequence][edge.canonical_range[1] - edge.node_to.depth: edge.canonical_range[1]])}\" appears {node_occurrences} times at positions: {edge.node_to.starting_positions}.')
                    self.find_patterns_longer_than_length_appear_more_than_n_times(length, n_times, edge.node_to)


if __name__ == '__main__':
    # Instantiating GOST
    t = SuffixTree()
    # Adding a sequence to GOST (without specification, the sequence_index will be 'sequence0')
    t.add_sequence('abananaandanananasandtwobananasandanananas')
    t.add_sequence('miss', 'state')
    # Appending to the sequence 'state'
    t.add_sequence('ississippi', 'state')
    # Print the tree
    t.draw_tree()
    # Interact with the tree (up to the active_points: the results presented here will be missing everything
    # that has yet to be inserted because of an active_point being on an edge. If you want to include those,
    # there are two options: adding a final character to every sequence, or recursively build the suffix trees of
    # the non covered parts)
    t.find_patterns_appear_more_than_n_times(10)
    t.find_patterns_longer_than_length_appear_more_than_n_times(5, 3)
    t.is_pattern_present('ananas')
