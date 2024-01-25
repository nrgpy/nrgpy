# Building docs

## Requirements

Install the docs requirements with

`pip install .[docs]`

## To build docs

```bash
~: cd [this directory]
~: sphinx-apidoc -f -o source/ ../
~: sphinx-build -b html source/ .
```
