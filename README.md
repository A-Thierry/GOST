# GOST
A Generalized Online Suffix Tree algorithm

Based on [Ukkonen's algorithm](https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf) ([or here for more explanations](https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english)). That's the Suffix Tree part. But GOST is:
* Generalized: one tree is used for multiple strings.
* Online: any of the strings can be extended and the tree will be updated.

## Output

![good old Mississippi](https://github.com/A-Thierry/GOST/blob/master/files/output.png)
One might notice that there is an occurence of 'i' missing at position 10: the active point is there, and that will be updated on the next step of the algorithm.

## Algorithm

For the first sequence, GOST works like Ukkonen's algorithm. Because GOST builds one suffix tree for multiple sequences, each sequence will have an index, 'sequence_index'.
As in Ukkonen's algorithm, we need to store those sequences: here in a dictionary ('sequences'). When appending a character to one sequence, one must specify to which, and that information is stored in 'active_sequence'. The same goes for edges: on top of the range they hold in the sequence, will have a 'canonical_sequence' attribute.

For the other sequences, we will start with an active point on the root node, which moves on the tree the same way  an active point moves in Ukkonen's algorithm (one per string, stored in the dictionary 'active_points', indexed with their respective 'sequence_index'). If the character we try to insert is not accessible from the active point, we will split an edge, create one, follow any accessible suffix link... depending on where that active point is, as described in Ukkonen's algorithm.

In Ukkonen's algorithm, the active point cannot reach a leaf. GOST, on the other hand, can have a sequence which is the suffix of another one (or has another one as a suffix, depending on which order those sequences are inserted), and that situation can arise. But, what is a leaf ? It's a node that represent the end of a sequence. Hence the edge leading to it must have the 'EndOfSequence' as its right interval born. Reaching a leaf means the active point was on such an edge: the sequence referenced on that edge and the one we are inserting have a common suffix longer than that edge (or the active point wouldn't be on the leaf), and we can swipe the references on it from its original sequence to the one we are inserting (references, plural cause that includes the range). It also means that the original sequence ends there, and in case we want to append to that sequence later on, we need to store a pointer to where in that edge: the character we will insert then won't necessary be the same as the one we are inserting now. Those will be stored in the 'Floating_leaves' class, in a dictionary indexed on the sequence_index. We then reset the active point to the root, reduce the remainder by one, and continue from there on in Ukkonen's fashion (or follow the suffix link from the node the edge came from). When inserting a character on a sequence that has floating leaves, we have to check that move them as we would active points.

## A note on complexity

This wont be a thorough analysis:
GOST is sensitive to the way the sequences are fed. If they are given sequentially: first sequence 1, then sequence 2.... It should perform the same as any generalized Ukkonen (with a special EndOfSequence for each sequence), as the number of floating leaves operation will remain low.
But feeding GOST the same sequence twice, with one character for the first index, and then two characters at a time alternating between them (and starting with the other index) will see a number of operations on its floating leaves in the O(n^2)... not that good. Or is-it ? The fact that the 'order' the sequences are given matters asks the question of the size of an instance: is it the sum of their length or their product ?

## Motivation

This is my attempt at an Online Generalized Suffix Tree algorithm.
The purpose of this implementation is to have a human readable version of the algorithm, and to hunt down for bugs.

## Tests

Try adding new strings or extending the ones at the end of [Tests.py](https://github.com/A-Thierry/GOST/blob/master/files/Tests.py).

## Contributing

Please read [CONTRIBUTING.md](https://github.com/A-Thierry/GOST/blob/master/CONTRIBUTING.md) for details on the code of conduct, and the process for submitting pull requests.

## Authors

* **Adrien Thierry** - *Initial work* -

## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](https://github.com/A-Thierry/GOST/blob/master/LICENSE) file for details
