# Polypheny Extension for IPython
This IPython extension adds `%poly` magics for querying a [Polypheny](https://polypheny.org/) polystore.  
The extension was heavily inspired by the [IPython SQL Extension](https://github.com/catherinedevlin/ipython-sql).

## Installation
### Requirements
Required Packages:
- ipython
- requests
- json

Optional Packages:
- pandas

### Get it PyPI
The package is not yet available on [PyPI](https://pypi.org/).

### Building & Installing the Package
From the top level directory, first execute `python -m build`.  
This should create a `.tar.gz` and `.whl` file in `dist/`.  
Now you can install the built package with `python -m pip install ./dist/<file-name>.whl`

### For Development
Since installation of a package is usually not needed for development, it can be installed in editable mode:  
Execute `python -m pip install -e .` from the top level folder of the project.

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

Storing the result in a variable:
```python
result = _

# Or when using line magics (note the now mandatory colon):
result = %poly sql: SELECT * FROM emps
```

Additionally to the query language, a namespace can be specified. 
It is also possible to set flags. The `-c` flag deactivates the cache for this query.:
```python
%%poly mql mynamespace -c
db.emps.find({})
```

### Advanced Functionality
The result object provides useful ways to work with the retrieved data.  
Provided [Pandas](https://pypi.org/project/pandas/) is installed, it is possible to transform the result in a `DataFrame`:
```python
result = %poly sql: SELECT * FROM emps
df = result.as_df()
```

### Planned Features
The following features are not yet implemented.

It should be possible to inject variables defined in the local namespace into a query:
```python
x = 10000
%% poly sql: SELECT * FROM emps WHERE salary > ${x}
```
The syntax for specifying variables in a query is not yet final.

## License
The Apache 2.0 License
