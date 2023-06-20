import json
from typing import Union, List
from prettytable import PrettyTable, PLAIN_COLUMNS


def build_result(raw_result: Union[str, dict, List[dict]]):
    result_set = get_result_dict(raw_result)

    if 'error' in result_set:
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


class QueryPolyResult(list):
    def __init__(self, result_set):
        self.result_set = result_set
        self.type = result_set['namespaceType']
        self._header = result_set['header']
        self._data = result_set['data']
        self.keys = [col['name'] for col in self._header]
        self._pretty = PrettyTable(self.keys)
        self._pretty.add_rows(self._data)
        self._pretty.set_style(PLAIN_COLUMNS)
        super().__init__(self._data)

    def __repr__(self):
        return self._pretty.get_string()

    def _repr_html_(self):
        return self._pretty.get_html_string()

    def dicts_list(self):
        return [dict(zip(self.keys, row)) for row in self._data]

    def dicts(self):
        for row in self._data:
            yield dict(zip(self.keys, row))

    def as_df(self):
        import pandas as pd  # only import pandas if required
        return pd.DataFrame.from_records(self._data, columns=self.keys)


class InfoPolyResult:
    def __init__(self, result_set):
        self.result_set = result_set

    def __repr__(self):
        rows = ['Successfully executed:',
                'Query:'.ljust(30) + str(self.result_set['generatedQuery'])
                ]
        return "\n".join(rows)


class ErrorPolyResult:
    def __init__(self, result_set):
        self.result_set = result_set

    def __repr__(self):
        rows = ['ERROR:',
                'Query:'.ljust(30) + str(self.result_set['generatedQuery']),
                'Message:'.ljust(30) + str(self.result_set['error'])
                ]
        return "\n".join(rows)
