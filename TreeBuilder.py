# This is my attempt at an Online Generalized Suffix Tree algorithm.
# Based on Ukkonen's algorithm (https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf)
# See also: https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english
# That's the Suffix Tree part.
# Generalized: one tree is used for multiple strings.
# Online: any of the strings referenced can be extended and the tree will be updated.
# I started this project because I needed an online implementation of an online suffix tree algorithm in python for
# work, and couldn't find any. I lost my job (time to look for a new one), but I had some fun generalizing it.
# It is not optimized: the purpose of this implementation is to have a human readable version of the algorithm,
# and to hunt for bugs.


class OnlineGeneralizedSuffixTree(object):
    """
     A class used to build generalized suffix tree online

     ...

     Attributes
     ----------
     sequences : {key=sequence_index:str,value=[s,e,q,u,e,n,c,e]}
         a dictionary of the sequences the suffix tree references:
     active_sequence : str
         reference to the sequence_index in 'sequences' we are inserting suffixes to
     active_points : {key=sequence_index, value=ActivePoint]
         dictionary of the different active points in the tree, indexed on their sequence_index
     created_nodes_during_step : [Nodes]
         list of the nodes created during one step of the algorithm

     Methods
     -------
     length(edge)
         return the length of an edge
     insert_suffix()
         insert the last character of the string 'self.sequences[self.active_sequence]' in the tree
     split_edge(old_edge, active_point):
         add the node 'middle_node' to the edge 'old_edge' at the position the active point 'active_point'
         is pointing at, add a new edge to that node.
     add_edge(node_from, canonical_range_from, canonical_range_to):
         add a new edge to the node 'node_from'. The new edge's canonical
         range is [canonical_range_from, canonical_range_to]
     update_after_split():
         set the active_point to the end of the suffix link starting in active_point.active_node,
         if any, otherwise set the active node to the root and the active edge to the one starting
         with the first character of the suffix we want to insert
     update_active_edge():
         select the next active_edge in case active_length is longer than the length of the current active_edge
     solve_unresolved_leaves():
         move the unresolved leafs along their respective edges/nodes and split the edge if an edge doesn't
         match the inserted character
     """

    def __init__(self, sequences=None, active_sequence='sequence0', active_points=None, created_nodes_during_step=None):
        """
        Parameters
        ----------
        sequences : list[str]
            a list of the sequences the tree is indexing
        active_sequence : str
            the index of the sequence we are actively inserting a suffix to in the list of sequences 'sequences'
        active_points: [ActivePoint]
            list of the active points of the tree corresponding to the different sequences (same index as 'sequences')
        created_nodes_during_step: [Node]
        """

        if sequences is None:
            sequences = {}
        self.sequences = sequences
        self.active_sequence = active_sequence
        self.root = self.Node(depth=0)
        if active_points is None:
            active_points = {}
        self.active_points = active_points
        if created_nodes_during_step is None:
            created_nodes_during_step = []
        self.created_nodes_during_step = created_nodes_during_step

    class Node(object):
        """
        A class used to represent the nodes in the generalized online suffix tree
        ...
        Attributes
        ----------
        edges: [Edge]
            list of outgoing edges
        incoming_edge: Edge
            incoming edge
        suffix_link_to: Node
            node to which there is a suffix link starting from that node
        depth: int
            length of the suffix represented by a node (sum of the length of the edges on the path
            from the root to that node)
        starting_positions: {sequence_index: [int]}
            list of the starting positions of the suffix in the different sequences (indexed as sequences)
        """

        def __init__(self, edges=None, incoming_edge=None, suffix_link_to=None, depth: int = -1, starting_positions=None):
            """
            Parameters
            ----------
            edges: [Edge]
                list of outgoing edges
            incoming_edge: Edge
                incoming edge
            suffix_link_to: Node
                node to which there is a suffix link starting from that node
            depth: int
                length of the suffix represented by a node (sum of the length of the edges on the path
                from the root to that node)
            starting_positions: {sequence_index: [int]}
                list of the starting positions of the suffix in the different sequences (indexed as sequences)
            """

            if edges is None:
                edges = []
            self.edges = edges
            self.incoming_edge = incoming_edge
            if suffix_link_to is None:
                suffix_link_to = []
            self.suffix_link_to = suffix_link_to
            self.depth = depth
            if starting_positions is None:
                starting_positions = {}
            self.starting_positions = starting_positions

    class Edge(object):
        """
        A class to represent the edges in the online generalized suffix tree
        ...
        Attributes
        ----------
        node_from: Node
                node the edge is coming from
        node_to: Node
            node the edge is pointing at
        canonical_range: [int]
            range of the array of elements in the sequence 'canonical_sequence' the edge
            represents (-1 for the end of the array)
        canonical_sequence: str
            index of the sequence in 'sequences' the edge is referring to
        unresolved_leaves: [UnresolvedLeaf]
            list of unresolved leaves standing on edge
        """

        def __init__(self, node_from=None, node_to=None, canonical_range=None, canonical_sequence='sequence0', unresolved_leaves=None):

            """
            Parameters
            ----------
            node_from: Node
                node the edge is coming from
            node_to: Node
                node the edge is pointing at
            canonical_range: [int]
                range of the array of elements in the sequence 'canonical_sequence' the edge
                represents (-1 for the end of the array)
            canonical_sequence: str
                index of the sequence in 'sequences' the edge is referring to
            unresolved_leaves: [UnresolvedLeaf]
                list of unresolved leaves standing on edge
            """

            self.node_from = node_from
            self.node_to = node_to
            if canonical_range is None:
                canonical_range = [None, -1]
            self.canonical_range = canonical_range
            self.canonical_sequence = canonical_sequence
            if unresolved_leaves is None:
                unresolved_leaves = []
            self.unresolved_leaves = unresolved_leaves

    def length(self, edge):
        """ Return the length of the edge 'edge' """
        if edge.canonical_range[1] == -1:
            return int(len(self.sequences[edge.canonical_sequence]) - int(edge.canonical_range[0]))
        else:
            return int(edge.canonical_range[1] - edge.canonical_range[0])

    class ActivePoint(object):
        """
        There is one active_point per sequence (the sequence indexed in 'sequences' with
        the same index as active_points in self.active_points)
        ...
        Attributes
        ----------
        active_node: Node
            active node
        active_edge: Edge
            active edge
        active_length: int
            active length
        current_point: int
            index in the sequence we are currently trying to match
        remainder: int
            number of suffixes to insert in the tree for that sequence
        unresolved_leaves: [UnresolvedLeaf]
            list of the unresolved leaves for the sequence the active point is referencing to
        """

        def __init__(self, active_node=None, active_edge=None, active_length: int = 0, current_point: int = 0, remainder: int = 0, created_nodes_during_step=None, unresolved_leaves=None):
            """
            Parameters
            ----------
            active_node: Node
                active node
            active_edge: Edge
                active edge
            active_length: int
                active length
            current_point: int
                index in the sequence we are currently trying to match
            remainder: int
                number of suffixes to insert in the tree for that sequence
            """

            self.active_node = active_node
            self.active_edge = active_edge
            self.active_length = active_length
            self.current_point = current_point
            self.remainder = remainder
            if created_nodes_during_step is None:
                created_nodes_during_step = []
            self.created_nodes_during_step = created_nodes_during_step
            if unresolved_leaves is None:
                unresolved_leaves = []
            self.unresolved_leaves = unresolved_leaves

    class UnresolvedLeaf(object):
        """
        A class used to represent the unresolved leaves in the online generalized suffix tree
        ...
        Attributes
        ----------
        node: Node
            the node the unresolved leaf is on
        edge: Edge
            the edge the unresolved leaf is on
        length: int
            the length on edge the unresolved leaf stands at
        sequence: str
            the index of the sequence the UnresolvedLeaf refers to
        """

        def __init__(self, node=None, edge=None, length: int = 0, current_point: int = 0, sequence='sequence0'):
            """
            Parameters
            node: Node
                the node the unresolved leaf is on
            edge: Edge
                the edge the unresolved leaf is on
            length: int
                the length on edge the unresolved leaf stands at
            sequence: str
                the index of the sequence the UnresolvedLeaf refers to
            """

            self.node = node
            self.edge = edge
            self.length = length
            self.current_point = current_point
            self.sequence = sequence

    def insert_suffix(self):
        """Insert the last character of the string 'self.sequences[self.active_sequence]' in the tree"""
        # Update the active point and the unresolved leaves
        if self.active_points[self.active_sequence].active_edge:
            self.update_active_edge()
        if self.active_points[self.active_sequence].unresolved_leaves:
            self.solve_unresolved_leaves()
        # If there is no active edge, select the one from 'self.active_point[self.active_sequence].active_node'
        # that starts with the character we want to insert. Create one if no one does.
        if self.active_points[self.active_sequence].active_edge is None:
            if self.active_points[self.active_sequence].active_node.edges:
                for edge in self.active_points[self.active_sequence].active_node.edges:
                    if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][len(self.sequences[self.active_sequence]) - 1]:
                        self.active_points[self.active_sequence].active_edge = edge
                        self.active_points[self.active_sequence].active_length = 1
                        return
            self.add_edge(node_from=self.active_points[self.active_sequence].active_node, starting_position=len(self.sequences[self.active_sequence]) - self.active_points[self.active_sequence].active_node.depth - 1)
            self.active_points[self.active_sequence].remainder -= 1
            self.update_after_split()
            if self.active_points[self.active_sequence].remainder >= 1:
                self.insert_suffix()
        # If there is an active edge, check if the next character on it matches the one we want to insert.
        # If it doesn't, split the edge to create a new branch (ie: insert a new suffix in the tree),
        # and calls itself recursively if the remainder calls for it (>0)
        else:
            if self.sequences[self.active_points[self.active_sequence].active_edge.canonical_sequence][self.active_points[self.active_sequence].active_edge.canonical_range[0] + self.active_points[self.active_sequence].active_length] == self.sequences[self.active_sequence][len(self.sequences[self.active_sequence]) - 1]:
                self.active_points[self.active_sequence].active_length += 1
                return
            else:
                self.split_edge(old_edge=self.active_points[self.active_sequence].active_edge, active_point=self.active_points[self.active_sequence])
                self.active_points[self.active_sequence].remainder -= 1
                self.update_after_split()
                if self.active_points[self.active_sequence].remainder >= 1:
                    self.insert_suffix()

    def split_edge(self, old_edge, active_point):
        """Add the node 'middle_node' to the edge 'old_edge' at the position the
        active point 'active_point' is pointing at, add a new edge to that node.
        Effectively: old_edge is shrunk and now points to 'middle_node', two new edges
         exit the later; one to complete old_edge, the other as a result of the split."""
        # set up length and edge depending on the type of active_point
        if active_point.__class__.__name__ == 'ActivePoint':
            length = active_point.active_length
            edge = active_point.active_edge
        else:
            length = active_point.length
            edge = active_point.edge
        middle_node = self.Node()
        # Deal with the starting positions of the different nodes involved
        middle_node.starting_positions = {starting_position: [starting_index for starting_index in old_edge.node_to.starting_positions[starting_position]] for starting_position in old_edge.node_to.starting_positions}
        middle_node.depth = old_edge.node_from.depth + length
        starting_position = len(self.sequences[self.active_sequence]) - middle_node.depth - 1
        if self.active_sequence not in middle_node.starting_positions:
            middle_node.starting_positions[self.active_sequence] = []
        middle_node.starting_positions[self.active_sequence].append(starting_position)
        self.add_edge(node_from=middle_node, starting_position=starting_position)
        new_edge = self.Edge(middle_node, old_edge.node_to, [old_edge.canonical_range[0] + length, old_edge.canonical_range[1]], old_edge.canonical_sequence)
        middle_node.edges.append(new_edge)
        old_edge.node_to.incoming_edge = new_edge
        old_edge.canonical_range[1] = old_edge.canonical_range[0] + length
        # Check if no other active points or unresolved leaves are on 'old_edge', if so, deal with them
        # depending on where they are relative to the split: before, do nothing; at the split, put them
        # on the new node, 'middle_node'; and put them on the new edge 'new_edge' if they come after.
        for unresolved_leaf in old_edge.unresolved_leaves:
            if unresolved_leaf.length > length:
                unresolved_leaf.length -= length
                unresolved_leaf.edge = new_edge
                if unresolved_leaf.sequence not in middle_node.starting_positions:
                    middle_node.starting_positions[unresolved_leaf.sequence] = []
                middle_node.starting_positions[unresolved_leaf.sequence].append(len(self.sequences[unresolved_leaf.sequence]) - middle_node.depth - unresolved_leaf.length)
                new_edge.unresolved_leaves.append(unresolved_leaf)
                old_edge.unresolved_leaves.remove(unresolved_leaf)
        unresolved_active_points_indices = []
        for active_sequence in self.sequences:
            if active_sequence == edge.canonical_sequence:
                break
            if self.active_points[active_sequence].active_edge is old_edge:
                if self.active_points[active_sequence].active_length == self.length(edge):
                    self.active_points[active_sequence].active_node = middle_node
                    self.active_points[active_sequence].active_edge = None
                    self.active_points[active_sequence].active_length = 0
                if self.active_points[active_sequence].active_length > self.length(edge):
                    self.active_points[active_sequence].active_length -= self.length(edge)
                    unresolved_active_points_indices.append(active_sequence)
        old_edge.node_to = middle_node
        middle_node.incoming_edge = old_edge
        while unresolved_active_points_indices:
            self.active_points[unresolved_active_points_indices.pop(0)].active_edge = new_edge

    def add_edge(self, node_from, canonical_range_from=None, canonical_range_to=None, starting_position=0):
        """ Add a new edge to a new node from node 'node_from'.
        new_edge.canonical_range = [canonical_range_from, canonical_range_to] """
        new_node = self.Node()
        if canonical_range_from is None:
            canonical_range = [len(self.sequences[self.active_sequence]) - 1, -1]
        else:
            if canonical_range_to is None:
                canonical_range_to = -1
            canonical_range = [canonical_range_from, canonical_range_to]
        new_edge = self.Edge(node_from, new_node, canonical_range, self.active_sequence)
        node_from.edges.append(new_edge)
        new_node.incoming_edge = new_edge
        new_node.starting_positions[self.active_sequence] = []
        new_node.starting_positions[self.active_sequence].append(starting_position)
        # Setting up suffix links in Ukkonen's fashion
        if self.created_nodes_during_step and node_from != self.root:
            self.created_nodes_during_step[0].suffix_link_to = node_from
            self.created_nodes_during_step.pop(0)
        self.created_nodes_during_step.append(node_from)

    def update_after_split(self):
        """ Follow suffix link if any, otherwise, set the active node to the root and the active edge
        to the one starting with the first character of the suffix we want to insert """
        # Follow suffix link if any:
        if self.active_points[self.active_sequence].active_node.suffix_link_to:
            self.active_points[self.active_sequence].active_node = self.active_points[self.active_sequence].active_node.suffix_link_to
            active_node = self.active_points[self.active_sequence].active_node
            # Add starting positions to the nodes not traversed thanks to suffix link
            while self.active_points[self.active_sequence].active_node != self.root:
                if self.active_sequence not in self.active_points[self.active_sequence].active_node.starting_positions:
                    self.active_points[self.active_sequence].active_node.starting_positions[self.active_sequence] = []
                self.active_points[self.active_sequence].active_node.starting_positions[self.active_sequence].append(len(self.sequences[self.active_sequence]) - active_node.depth - 1 - self.active_points[self.active_sequence].active_length)
                self.active_points[self.active_sequence].active_node = self.active_points[self.active_sequence].active_node.incoming_edge.node_from
            self.active_points[self.active_sequence].active_node = active_node
            # # Update the active edge in case the suffix link led to a more complicated branch
            if self.active_points[self.active_sequence].active_edge:
                for edge in self.active_points[self.active_sequence].active_node.edges:
                    if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_points[self.active_sequence].active_edge.canonical_sequence][self.active_points[self.active_sequence].active_edge.canonical_range[0]]:
                        self.active_points[self.active_sequence].active_edge = edge
                        break
                self.update_active_edge()
                return
        # Otherwise, set the active node to the root and the active edge to the one starting with the
        # first character of the suffix we want to insert
        else:
            self.active_points[self.active_sequence].active_node = self.root
            self.active_points[self.active_sequence].current_point = len(self.sequences[self.active_sequence]) - self.active_points[self.active_sequence].remainder
            if self.active_points[self.active_sequence].remainder >= 1:
                for edge in self.root.edges:
                    if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][self.active_points[self.active_sequence].current_point]:
                        self.active_points[self.active_sequence].active_edge = edge
                        self.active_points[self.active_sequence].active_length = self.active_points[self.active_sequence].remainder - 1
                        return
            self.active_points[self.active_sequence].active_edge = None

    def update_active_edge(self):
        """ Select the next active_edge in case active_length is longer than the length
        of the current active_edge (after following a suffix link, or if the insertion of
        another sequence split the edge the active_point is on) """
        while self.active_points[self.active_sequence].active_length >= self.length(edge=self.active_points[self.active_sequence].active_edge):
            # If the node at the end of active_edge is a leaf (end of a sequence), change the sequence that edge is
            # referencing and store a special pointer to that leaf: an UnresolvedLeaf
            if self.active_points[self.active_sequence].active_edge.canonical_range[1] == -1:
                unresolved_leaf = self.UnresolvedLeaf(edge=self.active_points[self.active_sequence].active_edge, node=None, length=self.length(edge=self.active_points[self.active_sequence].active_edge), current_point=len(self.sequences[self.active_points[self.active_sequence].active_edge.canonical_sequence]), sequence=self.active_points[self.active_sequence].active_edge.canonical_sequence)
                self.active_points[self.active_points[self.active_sequence].active_edge.canonical_sequence].unresolved_leaves.append(unresolved_leaf)
                self.active_points[self.active_sequence].active_edge.unresolved_leaves.append(unresolved_leaf)
                self.active_points[self.active_sequence].active_edge.node_to.starting_positions[self.active_points[self.active_sequence].active_edge.canonical_sequence] = []
                self.active_points[self.active_sequence].active_edge.canonical_sequence = self.active_sequence
                self.active_points[self.active_sequence].active_edge.canonical_range[0] = self.active_points[self.active_sequence].current_point
                if self.active_sequence not in self.active_points[self.active_sequence].active_edge.node_to.starting_positions:
                    self.active_points[self.active_sequence].active_edge.node_to.starting_positions[self.active_sequence] = []
                self.active_points[self.active_sequence].active_edge.node_to.starting_positions[self.active_sequence].append(len(self.sequences[self.active_sequence]) - self.active_points[self.active_sequence].remainder)
                self.active_points[self.active_sequence].remainder -= 1
                # follow suffix link if any
                if self.active_points[self.active_sequence].active_edge.node_from.suffix_link_to:
                    self.active_points[self.active_sequence].active_node = self.active_points[self.active_sequence].active_edge.node_from.suffix_link_to
                    for edge in self.active_points[self.active_sequence].active_node.edges:
                        if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][self.active_points[self.active_sequence].current_point]:
                            self.active_points[self.active_sequence].active_edge = edge
                            break
                # or set the active_point to the root, and select the active_edge starting with the first
                # character of the suffix we want to insert
                else:
                    self.active_points[self.active_sequence].active_node = self.root
                    self.active_points[self.active_sequence].active_length = self.active_points[self.active_sequence].remainder - 1
                    self.active_points[self.active_sequence].current_point = len(self.sequences[self.active_sequence]) - self.active_points[self.active_sequence].remainder
                    if self.active_points[self.active_sequence].remainder > 1:
                        for edge in self.root.edges:
                            if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][-self.active_points[self.active_sequence].remainder]:
                                self.active_points[self.active_sequence].active_edge = edge
                                self.active_points[self.active_sequence].active_length = self.active_points[self.active_sequence].remainder - 1
                                break
            # If the node at the end of active_edge is not a leaf,
            else:
                # Move the 'active_point' to the node at the end of the active edge, update the 'active_length'
                self.active_points[self.active_sequence].active_node = self.active_points[self.active_sequence].active_edge.node_to
                self.active_points[self.active_sequence].active_length -= self.length(edge=self.active_points[self.active_sequence].active_edge)
                self.active_points[self.active_sequence].current_point += self.length(edge=self.active_points[self.active_sequence].active_edge)
                if self.active_sequence not in self.active_points[self.active_sequence].active_node.starting_positions:
                    self.active_points[self.active_sequence].active_node.starting_positions[self.active_sequence] = []
                self.active_points[self.active_sequence].active_node.starting_positions[self.active_sequence].append(min(len(self.sequences[self.active_sequence]) - 1 - self.active_points[self.active_sequence].active_node.depth - self.active_points[self.active_sequence].active_length, self.active_points[self.active_sequence].current_point - 1))
                # Select the next active_edge and call itself recursively if active_length is not zero
                if self.active_points[self.active_sequence].active_length >= 1:
                    for edge in self.active_points[self.active_sequence].active_node.edges:
                        if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][self.active_points[self.active_sequence].current_point]:
                            self.active_points[self.active_sequence].active_edge = edge
                            break
        # Ensure there is no active_edge if active_length is zero
        if self.active_points[self.active_sequence].active_length == 0:
            self.active_points[self.active_sequence].active_edge = None
            return

    def solve_unresolved_leaves(self):
        """ Move the unresolved leafs along their respective edges/nodes and
         split the edge if an edge doesn't match the inserted character."""
        leaves_to_remove = []
        add_suffix_link_from = []
        # For each unresolved_leaf of the active_sequence:
        if self.active_points[self.active_sequence].unresolved_leaves:
            self.active_points[self.active_sequence].unresolved_leaves.sort(key=lambda x: x.edge.node_from.depth + x.length, reverse=True)
            # todo self.active_points[self.active_sequence].unresolved_leaves should already be sorted.
            # todo Should be thoroughly checked and then get rid of the sorting step
            for leaf in self.active_points[self.active_sequence].unresolved_leaves:
                # if the unresolved_leaf is in the middle of an edge:
                if self.length(edge=leaf.edge) > leaf.length:
                    # Move the unresolved_leaf along the edge if the next character along the
                    # edge matches the one we are inserting
                    if self.sequences[leaf.edge.canonical_sequence][leaf.edge.canonical_range[0] + leaf.length] == self.sequences[self.active_sequence][-1]:
                        leaf.length += 1
                    # Split the edge at the point the unresolved_leaf if the character along the edge
                    # doesn't match the one we are inserting, unresolved_leaf is resolved
                    else:
                        leaves_to_remove.append(leaf)
                        self.split_edge(old_edge=leaf.edge, active_point=leaf)
                        # Set up suffix links
                        if add_suffix_link_from:
                            if add_suffix_link_from[0].depth == leaf.edge.node_to.depth + 1:
                                add_suffix_link_from.pop(0).suffix_link_to = leaf.edge.node_to
                            else:
                                add_suffix_link_from = []
                        add_suffix_link_from.append(leaf.edge.node_to)
                # if the unresolved_leaf is at the end of an edge:
                elif self.length(edge=leaf.edge) == leaf.length:
                    # if the node at the end of the edge is a leaf: swap for which leaf is
                    # unresolved and which is resolved
                    if leaf.edge.canonical_range[1] == -1:
                        unresolved_leaf = self.UnresolvedLeaf(edge=leaf.edge, node=None, length=self.length(edge=leaf.edge), current_point=len(self.sequences[leaf.edge.canonical_sequence]), sequence=leaf.edge.canonical_sequence)
                        self.active_points[leaf.edge.canonical_sequence].unresolved_leaves.append(unresolved_leaf)
                        leaves_to_remove.append(leaf)
                        leaf.edge.unresolved_leaves.append(unresolved_leaf)
                        leaf.edge.node_to.starting_positions[leaf.edge.canonical_sequence] = []
                        leaf.edge.canonical_sequence = self.active_sequence
                        leaf.edge.node_to.starting_positions[self.active_sequence].append(len(self.sequences[self.active_sequence]) - (leaf.edge.node_from.depth + self.length(leaf.edge)))
                        leaf.edge.canonical_range[0] = len(self.sequences[self.active_sequence]) - self.length(leaf.edge)
                        leaf.edge.canonical_range[1] = -1
                    # otherwise, select the next edge unresolved_leaf will be on if such an edge
                    # matches with the character we want to insert
                    else:
                        if leaf.sequence not in leaf.edge.node_to.starting_positions:
                            leaf.edge.node_to.starting_positions[leaf.sequence] = []
                        leaf.edge.node_to.starting_positions[leaf.sequence].append(len(self.sequences[self.active_sequence]) - leaf.edge.node_to.depth - 1)
                        r = leaf.edge
                        for edge in leaf.edge.node_to.edges:
                            if self.sequences[edge.canonical_sequence][edge.canonical_range[0]] == self.sequences[self.active_sequence][-1]:
                                leaf.current_point += self.length(edge=leaf.edge)
                                leaf.edge = edge
                                leaf.length = 1
                                break
                        # or create an edge if no such edge exists (unresolved_leaf is resolved)
                        if leaf.edge == r:
                            self.add_edge(node_from=leaf.edge.node_to, canonical_range_from=len(self.sequences[self.active_sequence]) - 1, starting_position=len(self.sequences[self.active_sequence]) - leaf.edge.node_to.depth - 1)
                        del leaf
        while leaves_to_remove:
            leaf = leaves_to_remove.pop(0)
            self.active_points[self.active_sequence].unresolved_leaves.remove(leaf)
            leaf.edge.unresolved_leaves.remove(leaf)
            del leaf
