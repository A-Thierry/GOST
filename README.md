# GOST
A Generalized Online Suffix Tree algorithm

Based on [Ukkonen's algorithm](https://www.cs.helsinki.fi/u/ukkonen/SuffixT1withFigs.pdf) ([or here for more explanations](https://stackoverflow.com/questions/9452701/ukkonens-suffix-tree-algorithm-in-plain-english)). That's the Suffix Tree part. But GOST is:
* Generalized: one tree is used for multiple strings.
* Online: any of the strings can be extended and the tree will be updated.

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
