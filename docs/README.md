To build docs:

```
~: cd [this directory]
~: sphinx-apidoc -f -o source/ ../
~: sphinx-build -b html source/ .