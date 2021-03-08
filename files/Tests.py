from Functions import SuffixTree


if __name__ == '__main__':

    # Instantiating GOST
    t = SuffixTree()
    
    # Adding a sequence to GOST (without specification, the sequence_index will be 'sequence0', here the sequence is a string)
    t.add_sequence('abananaandanananas')
    # Adding another sequence to GOST (sequence_index is 'state', here the sequence is a list)
    t.add_sequence(['m', 'i', 's', 's'], 'river')
    # Appending to the sequence 'state'
    t.add_sequence(['i', 's', 's', 'i', 's', 's', 'i', 'p', 'p', 'i'], 'river')
    # Appending to the first sequence ('sequence0')
    t.add_sequence('and')
    t.add_sequence('twobananasandanananas')
    
    # Interacting with GOST
    print('\n'*3)
    t.draw_tree()
    t.find_patterns_appear_more_than_n_times(10)
    t.find_patterns_longer_than_length_appear_more_than_n_times(5, 3)
    t.is_pattern_present('ananas')
    # The results presented here will be missing everything that has yet to be inserted because of an active_point being
    # on an edge. If you want to include those, there are two options: adding a final character to every sequence, or
    # recursively build the suffix trees of the non covered parts)
