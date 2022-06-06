## requirements

use pip to install these packages or the below commands will fail:

- numpydoc
- sphinx
- sphinx-book-theme

## to build docs:

```
~: cd [this directory]
~: sphinx-apidoc -f -o source/ ../
~: sphinx-build -b html source/ .
