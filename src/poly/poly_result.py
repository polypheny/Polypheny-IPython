import pandas as pd
import abc


def build_result(result):
    if 'error' in result:
        return ErrorPolyResult(result)
    if 'header' not in result:
        return InfoPolyResult(result)

    ns = result['namespaceType']

    # TODO: Create Result Classes for Document and Graph
    if ns == 'RELATIONAL':
        return RelationalPolyResult(result)
    elif ns == 'DOCUMENT':
        return RelationalPolyResult(result)
    elif ns == 'GRAPH':
        return RelationalPolyResult(result)


class PolyResult(metaclass=abc.ABCMeta):

    def __init__(self, result):
        self.result = result

    def __repr__(self):
        return self.get_repr()

    @abc.abstractmethod
    def get_repr(self):
        pass

    @abc.abstractmethod
    def as_df(self):
        pass


class InfoPolyResult(PolyResult):
    def get_repr(self):
        rows = ['---- INFO ----',
                'Query:'.ljust(30) + str(self.result['generatedQuery']),
                'Affected Rows:'.ljust(30) + str(self.result['affectedRows']),
                'Namespace Type:'.ljust(30) + str(self.result['namespaceType'])
                ]
        return "\n".join(rows)

    def __init__(self, result):
        super().__init__(result)

    def as_df(self):
        raise ValueError('Result is not convertible into a DataFrame.')


class ErrorPolyResult(PolyResult):
    def get_repr(self):
        rows = ['---- ERROR ----',
                'Error:'.ljust(30) + str(self.result['error']),
                'Exception:'.ljust(30) + str(self.result['exception']),
                'Query:'.ljust(30) + str(self.result['generatedQuery']),
                'Affected Rows:'.ljust(30) + str(self.result['affectedRows']),
                'Namespace Type:'.ljust(30) + str(self.result['namespaceType'])
                ]
        return "\n".join(rows)

    def __init__(self, result):
        super().__init__(result)

    def as_df(self):
        raise ValueError('Error is not convertible into a DataFrame.')


class RelationalPolyResult(PolyResult):
    def get_repr(self):
        rows = ['---- RELATIONAL ----',
                'Query:'.ljust(30) + str(self.result['generatedQuery']),
                'Affected Rows:'.ljust(30) + str(self.result['affectedRows']),
                'Namespace Type:'.ljust(30) + str(self.result['namespaceType']),
                'Header:'.ljust(30) + str(self.result['header']),
                'Data:'.ljust(30) + str(self.result['data'])
                ]
        return "\n".join(rows)

    def __init__(self, result):
        super().__init__(result)

    def as_df(self):
        header = self.result['header']
        data = self.result['data']

        cols = map(lambda x: x['name'], header)

        return pd.DataFrame.from_records(data, columns=cols)
