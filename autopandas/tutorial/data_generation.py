import itertools
import pickle
import random

import pandas as pd
from atlas import generator
from atlas.strategies import DfsStrategy, operator
from atlas.synthesis.pandas.dataframe_generation import generate_random_dataframe, DfConfig
from typing import Collection, Any


class DataGenStrategy(DfsStrategy):
    @operator
    def Select(self, domain, **garbage):
        domain = list(domain)
        random.shuffle(domain)
        yield from domain

    @operator
    def Subset(self, domain: Any, context: Any = None, lengths: Collection[int] = None,
               include_empty: bool = False, **kwargs):
        if lengths is None:
            lengths = range(0 if include_empty else 1, len(domain) + 1)

        lengths = list(lengths)
        random.shuffle(lengths)
        domain = list(domain)
        random.shuffle(domain)

        for l in lengths:
            yield from itertools.combinations(domain, l)

    @operator
    def OrderedSubset(self, domain: Any, context: Any = None,
                      lengths: Collection[int] = None, include_empty: bool = False, **kwargs):

        if lengths is None:
            lengths = range(0 if include_empty else 1, len(domain) + 1)

        lengths = list(lengths)
        random.shuffle(lengths)
        domain = list(domain)
        random.shuffle(domain)

        for l in lengths:
            yield from itertools.permutations(domain, l)


def create_dataset(pivot_gen, num_datapoints: int):
    random.seed(0)
    dataset = []
    while len(dataset) < num_datapoints:
        df = generate_random_dataframe.call(DfConfig(index_levels=1, column_levels=1))
        s = DataGenStrategy()
        for result in pivot_gen.generate(df, None).with_strategy(s).with_tracing().first(k=10):
            if result is None:
                break

            args, trace = result
            try:
                out = df.pivot(**args)
                if 0 in out.shape:
                    continue

                _, trace = pivot_gen.generate(df, out).with_tracing().with_replay(trace).first()
                dataset.append(trace)
                break

            except:
                pass

    return dataset


def generate_data_pivot_columns():
    @generator
    def gen_pivot_args(input_df: pd.DataFrame, output_df: pd.DataFrame):
        # Select one of columns
        arg_columns = Select(list(input_df.columns), context=(input_df, output_df), uid="select_columns")
        # Select one of columns or None
        arg_index = Select([None] + [i for i in list(input_df.columns) if i != arg_columns])

        # Select one of columns or list of columns
        if Select([True, False]):
            arg_values = Select([None] + [i for i in list(input_df.columns) if i != arg_columns and i != arg_index])
        else:
            arg_values = list(OrderedSubset([i for i in list(input_df.columns)
                                             if i != arg_columns and i != arg_index]))

        return {'index': arg_index, 'columns': arg_columns, 'values': arg_values}

    dataset = create_dataset(gen_pivot_args, 600)
    with open('training_data_pivot_columns.pkl', 'wb') as f:
        pickle.dump(dataset, f)


def generate_data_pivot_full():
    @generator
    def gen_pivot_args(input_df: pd.DataFrame, output_df: pd.DataFrame):
        # Select one of columns
        arg_columns = Select(list(input_df.columns), context=(input_df, output_df))
        # Select one of columns or None
        arg_index = Select([None] + [i for i in list(input_df.columns) if i != arg_columns],
                           context=(input_df, output_df))

        # Select one of columns or list of columns
        if Select([True, False], context=(input_df, output_df), uid="branch"):
            arg_values = Select([None] + [i for i in list(input_df.columns) if i != arg_columns and i != arg_index],
                                context=(input_df, output_df))
        else:
            arg_values = list(OrderedSubset([i for i in list(input_df.columns) if i != arg_columns and i != arg_index],
                                            context=(input_df, output_df)))

        return {'index': arg_index, 'columns': arg_columns, 'values': arg_values}

    dataset = create_dataset(gen_pivot_args, 600)
    with open('training_data_pivot_full.pkl', 'wb') as f:
        pickle.dump(dataset, f)


if __name__ == "__main__":
    generate_data_pivot_columns()
    generate_data_pivot_full()
