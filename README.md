<p align="center">
    <a href="https://polypheny.org/">
        <picture><source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-white-text_cropped.png">
            <img width='50%' alt="Light: 'Resume application project app icon' Dark: 'Resume application project app icon'" src="https://raw.githubusercontent.com/polypheny/Admin/master/Logo/logo-transparent_cropped.png">
        </picture>
    </a>    
</p> 

# Polypheny Extension for IPython
This IPython extension adds `%poly` magics for querying [Polypheny](https://polypheny.org/) using any of the supported query languages. This extension takes inspiration from the brilliant [IPython SQL Extension](https://github.com/catherinedevlin/ipython-sql).

## Installation

### Via PyPi
The recommended way to install the package is with pip:
```bash
pip install ipython-polypheny
```

### From Source
If you do not want to use pip, you can download the code and build it manually.

1. Download the source code.
2. At the root directory, run python -m build. This will produce .tar.gz and .whl files in the dist/ folder.
3. Install the package using: python -m pip install ./dist/<file-name>.whl.

## Usage
Activate the extension using:
```python
%load_ext poly
```

You can utilize both line magics (%poly) and cell magics (%%poly). A command must always follow the magic keyword. For instance: 
```python
# Print help
%poly help
```

Commands requiring arguments should separate them using a colon (:):
```python
# Specify the http-interface address of a running Polypheny instance.
%poly db: http://localhost:13137
```

The colon can also be replaced by a line break when using cell magics.
This is the ideal syntax for querying the database, where the command specifies the query language:
```python
%%poly sql
SELECT * FROM emps
```
The result is automatically printed as a nicely formatted table.

Interact with the retrieved data in multiple ways:

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
The data can be accessed like a two-dimensional `list`:
```python
# get the value of the element in the first row and second column
result[0][1]
```
Iterate over the rows as `dict`s:
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

## Data Types
Polypheny's data types are mapped to Python's as follows:

| Type in Polypheny                          | Type in Python  |
|:-------------------------------------------|:----------------|
| `BIGINT`, `INTEGER`, `SMALLINT`, `TINYINT` | `int`           |
| `DECIMAL`, `DOUBLE`, `REAL`                | `float`         |
| `BOOLEAN`                                  | `bool`          |
| `DOCUMENT`, `JSON`, `NODE`, `PATH`         | `dict`          |
| `ARRAY`                                    | `list`          |

Other types are stored as str. Failed casting operations will also result in str.  If the raw data as a nested `list` of `str` is required, one can get it from the `ResultSet`:
```python
raw_data = result.result_set['data']
```

### Limitations
Working with multimedia and other blob types is currently not supported. While it does not result in an error, only the identifier is stored, not the actual content.


## Contributing
Thank you for considering contributing! We truly appreciate any effort, whether it's fixing bugs, improving documentation, or suggesting new features. Here's a guide to help streamline the process:

1. **Start by Forking**: Begin by forking the repository. Once done, you can work on your changes and then submit them as a pull request.

2. **Development Guidelines**: Before diving in, take a moment to explore our [Documentation](https://docs.polypheny.com). Pay special attention to the 'For Developers' section — it offers insights on setup, code style, organization, and other valuable resources tailored for developers.

3. **Adherence to Code of Conduct**: We are committed to fostering an open and welcoming environment. As such, we request all contributors to uphold the standards outlined in our [code of conduct](https://github.com/polypheny/Admin/blob/master/CODE_OF_CONDUCT.md) throughout their interactions related to the project.

4. **Setting up for Development**:
   - **Editable Installation**: To see your code changes reflected in real-time, install the extension in an editable mode. Execute the following command from the root directory of the extension:
     ```bash
     python -m pip install -e .
     ```
     This allows any modifications in the codebase to be instantly visible post-reloading the extension.
     
   - **Utilize Autoreload**: For a smoother development experience, consider activating the [autoreload](https://ipython.org/ipython-doc/3/config/extensions/autoreload.html) extension. This tool automatically reloads the extension and incorporates the recent code changes:
     ```python
     %load_ext autoreload
     %autoreload 2
     %load_ext poly
     ```

Thank you for your dedication and enthusiasm for enhancing the Polypheny ecosystem! We look forward to reviewing your valuable contributions.

## License
The Apache 2.0 License
