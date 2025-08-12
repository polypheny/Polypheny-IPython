import json
from typing import Union, List
from prettytable import PrettyTable, PLAIN_COLUMNS


def build_result(raw_result: Union[str, dict, List[dict]]):
    result_set = get_result_dict(raw_result)

    if result_set.get('error') is not None:
        return ErrorPolyResult(result_set)
    if 'header' not in result_set:
        return InfoPolyResult(result_set)

    return QueryPolyResult(result_set)


def get_result_dict(raw_result: Union[str, dict, List[dict]]) -> Union[None, dict]:
    if isinstance(raw_result, str):
        try:
            raw_result = json.loads(raw_result)
        except json.JSONDecodeError:
            return None
    if isinstance(raw_result, list):
        raw_result = raw_result[-1]  # return the last result_set if several results are present
    return raw_result


def get_type_from_string(type_string):
    cleaned = type_string.strip().upper()
    if cleaned in ['INTEGER', 'BIGINT', 'SMALLINT', 'TINYINT']:
        return int
    if cleaned == 'BOOLEAN':
        return bool
    if cleaned in ['DECIMAL', 'DOUBLE', 'REAL']:
        return float
    if cleaned in ['ARRAY', 'JSON', 'DOCUMENT', 'DOCUMENT NOT NULL']:
        return json.loads
    if cleaned.startswith('PATH') or cleaned.startswith('NODE') or cleaned.startswith('EDGE'):
        return json.loads
    return None


def cast_data(raw_data, header, data_model):
    if data_model in ['RELATIONAL', 'GRAPH']:
        data = [row[:] for row in raw_data]  # Create shallow copy
        data_types = [get_type_from_string(col['dataType']) for col in header]

        for col_idx, col_type in enumerate(data_types):
            if col_type is None:
                continue
            for row_idx in range(len(data)):
                try:
                    data[row_idx][col_idx] = col_type(data[row_idx][col_idx])
                except (TypeError, json.JSONDecodeError):
                    pass
    elif data_model == 'DOCUMENT':
        # transform documents to rows with 1 column
        data = [[json.loads(doc[0] if isinstance(doc, list) else doc)] for doc in raw_data]
    else:
        raise ValueError(f'Unsupported dataModel: {data_model}')
    return data


class QueryPolyResult(list):  # Data is stored in a nested list. For simplicity, we do not use Numpy, but Python lists
    def __init__(self, result_set):
        self.result_set = result_set
        self.type = result_set['dataModel']
        self._header = result_set['header']
        self.keys = [col['name'] for col in self._header]
        self._data = cast_data(result_set['data'], self._header, self.type)
        self._pretty = PrettyTable(self.keys)
        self._pretty.add_rows(self._data)
        self._pretty.set_style(PLAIN_COLUMNS)
        super().__init__(self._data)

    def __repr__(self):
        return self._pretty.get_string()

    def _repr_html_(self):
        return self._pretty.get_html_string()

    def dicts(self):
        return [dict(zip(self.keys, row)) for row in self._data]

    def as_df(self):
        import pandas as pd  # only import pandas if required
        return pd.DataFrame.from_records(self._data, columns=self.keys)


class InfoPolyResult:
    def __init__(self, result_set):
        self.result_set = result_set

    def __repr__(self):
        rows = ['Successfully executed:',
                'Query:'.ljust(30) + str(self.result_set['query'])
                ]
        return "\n".join(rows)


class ErrorPolyResult:
    def __init__(self, result_set):
        self.result_set = result_set

    def __repr__(self):
        rows = ['ERROR:',
                'Query:'.ljust(30) + str(self.result_set['query']),
                'Message:'.ljust(30) + str(self.result_set['error'])
                ]
        return "\n".join(rows)
