"""Script for extracting variables from tropical cyclone datafile
   Author: Shaun Lowis, for Bodeker Scientific
"""

import pandas as pd
import numpy as np
import dask.dataframe as dd


def reduce_mem_usage(df):
    """
    iterate through all the columns of a dataframe and
    modify the data type to reduce memory usage.
    """
    start_mem = df.memory_usage().sum() / 1024 ** 2
    print(('Memory usage of dataframe is {:.2f}'
           'MB').format(start_mem))

    for col in df.columns:
        col_type = df[col].dtype

        if col_type != object:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < \
                        np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < \
                        np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < \
                        np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < \
                        np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < \
                        np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < \
                        np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)
        else:
            df[col] = df[col].astype('category')
            end_mem = df.memory_usage().sum() / 1024 ** 2
    print(('Memory usage after optimization is: {:.2f}'
           'MB').format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem)
                                        / start_mem))

    return df




def read_csv(filepath):
    """Script for reading and sorting values into percentages of how full they are
    :param filepath: path to .csv file
    :return: List of how full each column is
    """
    df = pd.read_csv(filepath, low_memory=False, skiprows=[1])
    df = reduce_mem_usage(df)
    # header_list = df.columns.values.tolist()
    # datatypes = df.iloc[0]
    # # if type in header_list is float or type in datatypes is int:
    # #     s2 = df.aggregate(df, [df.rdiv(df, len(df)), ])
    # for header in header_list:
    #     if df[header].dtype == "int64" or df[header].dtype == "float64":
    #         s2 = header.aggregate(header, [header.rdiv(header, len(header)), ])
    #         print(s2)

    # df = dd.read_csv(filepath, dtype=object)

    # chunks = pd.read_csv(filepath, chunksize=10000)
    # data = pd.concat(chunks)
    # # data.info(memory_usage="deep")
    # print(data.info())

    # for val in data:
    #     if val.isnumeric is True:
    #         val.apply(pd.to_numeric, downcast='unsigned')
    #
    # s2 = data.aggregate(data, [data.rdiv(data, len(data)), ])
    #
    # print(s2)
    #
    # print(data)
    # print(data.get_dtype_counts())
    # s2 = data.aggregate(data, [data.rdiv(data, len(data)), ])
    # print(str(s2))


def main():

    csv_filepath = r"/home/shaun/Documents/EWERAM/ibtracs.ALL.list.v04r00.csv"
    read_csv(csv_filepath)


main()


# Links for this data:
# https://www.essl.org/cms/european-severe-weather-database/
# ftp://eclipse.ncdc.noaa.gov/pub/ibtracs/v04r00/doc/IBTrACS_v04_column_documentation.pdf
