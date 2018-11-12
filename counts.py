import argparse

from core.utils.directory_parsers import TopLevelDirectory
from core.utils.mutation_counters import convert_mutation_file_to_dataframe, merge_dataframes


def generate_merged_df(dir_name):
    top_level_directory = TopLevelDirectory(dir_name)
    merged_df = merge_dataframes([convert_mutation_file_to_dataframe(mut_file) for mut_file in
                                  top_level_directory.mutation_files])

    return merged_df


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', type=str, help='directory with file', required=True)
    parser.add_argument('--output', '-o', type=str, help='output file name', required=True)
    args = parser.parse_args()

    df = generate_merged_df(args.directory)

    with open(args.output, 'w') as f:
        df.to_csv(f, sep='\t', index=False)
