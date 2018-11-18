import os

import pandas as pd


def convert_mutation_file_to_dataframe(file_path):
    trimmed_df = _trim_and_rename_df(pd.read_csv(file_path, header=0, sep='\t'))
    positional_df = _expand_variant_info_column(trimmed_df)

    dirs, file_name = os.path.split(file_path)
    dir_with_info = dirs.split(os.sep)[-2]

    sample_name, oligo_number = _get_sample_name_and_oligo_number(dir_with_info)

    full_df = _add_columns(
        positional_df,
        *[('sample', sample_name), ('oligo', oligo_number), ('count', _get_count(file_name))]
    )
    full_df = full_df.reset_index()

    wanted_columns = ['chr', 'pos', 'ref', 'alt', 'sample', 'oligo', 'mutation', 'count']
    return full_df[wanted_columns]


def _trim_and_rename_df(df):
    df = df.rename(index=str, columns={'Erica_term': 'mutation'})
    return df[df['mutation'] != 'BARCODE']


def _expand_variant_info_column(df):
    df[['chr', 'pos', 'base_change']] = df['Variant'].str.split('_', expand=True)
    df[['ref', 'alt']] = df['base_change'].str.split('/', expand=True)

    return df


def _get_sample_name_and_oligo_number(dir_name_with_info):
    vcf_string, timepoint, sample_letter, oligo_name = dir_name_with_info.split('_')
    sample_name = '_'.join((timepoint, sample_letter))
    oligo_number = oligo_name.lstrip('oligo')

    return sample_name, oligo_number


def _add_columns(df, *name_value_tuples):
    for two_tuple in name_value_tuples:
        col_name, value = two_tuple
        df[col_name] = [value] * df.shape[0]

    return df


def _get_count(file_name):
    mut_string, sample_id, count = os.path.splitext(file_name)[0].split('_')
    return int(count)


def merge_dataframes(df_list, group_criteria=None):
    merged_df = df_list.pop(0)
    for next_df in df_list:
        merged_df = pd.concat((merged_df, next_df), axis=0, ignore_index=True)

    grouping = ['chr', 'pos', 'ref', 'alt']
    if group_criteria:
        grouping.extend(group_criteria)
    else:
        grouping.extend(['sample', 'oligo', 'mutation'])
    merged_df = merged_df.groupby(grouping, as_index=False).sum()
    return merged_df
