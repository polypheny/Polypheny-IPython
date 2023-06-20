# Polypheny Extension for IPython
This IPython extension adds `%poly` magics for querying a [Polypheny](https://polypheny.org/) polystore.  
The extension was heavily inspired by the [IPython SQL Extension](https://github.com/catherinedevlin/ipython-sql).

## Installation

### Get it via PyPI
The package is not yet available on [PyPI](https://pypi.org/).

### Building & Installing the Package
From the top level directory, first execute `python -m build`.  
This should create a `.tar.gz` and `.whl` file in `dist/`.  
Now you can install the built package with `python -m pip install ./dist/<file-name>.whl`.

### During Development
Since installation of a package is usually not needed for development, it can be installed in editable mode:  
Execute `python -m pip install -e .` from the top level folder of the project.

Changes to the codebase should now be reflected immediately after reloading the extension.  
It is useful to have [autoreload](https://ipython.org/ipython-doc/3/config/extensions/autoreload.html) running, to automatically reload the extension:
```python
%load_ext autoreload
%autoreload 2

%load_ext poly
```

## Usage
First, the extension needs to be loaded:
```python
%load_ext poly
```

Both line magics (lines starting with `%poly`) and cell magics (cells starting with`%%poly`) can be used.  
Following the magic keyword, a command must be specified.  

Here is a basic example:
```python
# Print help
%poly help
```

If a command expects an argument, then it must be separated with a colon (`:`):
```python
# Connect to the http-interface of a running Polypheny instance.
%poly db: http://localhost:13137
```

The colon can also be replaced by a line break when using cell magics.
This is the ideal syntax for querying the database, where the command specifies the query language:
```python
%%poly sql
SELECT * FROM emps
```
The result is automatically printed as a nicely formatted table.

Storing the result in a variable:
```python
result = _

# Or when using line magics (note the required colon that separates the query from the command):
result = %poly sql: SELECT * FROM emps
```

Additionally to the query language, a namespace can be specified. 
It is also possible to set flags. The `-c` flag deactivates the cache for this query:
```python
%%poly mql mynamespace -c
db.emps.find({})
```

### Working With the Result
The result object provides useful ways to work with the retrieved data.  
```python
result = %poly sql: SELECT * FROM emps
```
Getting the raw `ResultSet`:
```python
result.result_set
```
The data can be accessed like a two-dimensional list:
```python
# get the value of the element in the first row and second column
result[0][1]
```
Iterate over the rows as dicts:
```python
for employee in result.dicts():
    print(employee['name'], employee['salary'])
```


Provided [Pandas](https://pypi.org/project/pandas/) is installed, it is possible to transform the result into a `DataFrame`:
```python
df = result.as_df()
```

### Advanced Features

It is possible to expand variables defined in the local namespace into a query.
For this to work, the `--template` (shorter: `-t`) flag must be set:
```python
key = 'salary'
x = 10000

%% poly -t sql: SELECT * FROM emps WHERE ${key} > ${x}

# is equal to
%% poly sql: SELECT * FROM emps WHERE salary > 10000
```
Be careful to not accidentally inject unwanted queries, as the values are not escaped.

## License
The Apache 2.0 License
