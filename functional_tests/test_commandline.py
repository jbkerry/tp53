import os
import shutil
import tempfile
from unittest import TestCase

import pandas as pd

temp_dir = tempfile.mkdtemp()
test_dir = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(test_dir, '..', 'tests', 'resources')


class MainRunTest(TestCase):

    def setUp(self):
        directories = [
            os.path.join(temp_dir, '48hr_final', 'vcfs_48hr_C', 'vcfs_48hr_C_oligo3only'),
            os.path.join(temp_dir, '48hr_final', 'vcfs_48hr_C', 'vcfs_48hr_C_oligo2'),
            os.path.join(temp_dir, '12d_final2', 'vcfs_12d_B', 'vcfs_12d_B_oligo1T'),
            os.path.join(temp_dir, '12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1T'),
            os.path.join(temp_dir, '12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1G')
        ]
        for directory in directories:
            del_directory = os.path.join(directory, 'DELETERIOUS')
            non_del_directory = os.path.join(directory, 'NON-DELETERIOUS')
            os.makedirs(del_directory)
            os.makedirs(non_del_directory)
            for mut_file in os.listdir(resource_dir):
                shutil.copy(os.path.join(resource_dir, mut_file), del_directory)
                # shutil.copy(os.path.join(resource_dir, mut_file), non_del_directory)

    def test_normal_run(self):
        # Erica supplies a directory on the command-line via the -d flag
        # Erica supplies a output file name via the -o flag

        os.system('~/envs/py3.6/bin/python3 ~/Coding/tp53/counts.py -d {} -o {}'.format(
                  temp_dir, os.path.join(temp_dir, 'output.tsv')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'output.tsv')))

        rows = [
            [17, 7578424, 'A', 'C', '12d_B', '1T', 'DELETERIOUS', 4],
            [17, 7578424, 'A', 'C', '12d_C', '1G', 'DELETERIOUS', 4],
            [17, 7578424, 'A', 'C', '12d_C', '1T', 'DELETERIOUS', 4],
            [17, 7578424, 'A', 'C', '48hr_C', '2', 'DELETERIOUS', 4],
            [17, 7578424, 'A', 'C', '48hr_C', '3only', 'DELETERIOUS', 4],
            [17, 7578439, 'T', 'G', '12d_B', '1T', 'DELETERIOUS', 1],
            [17, 7578439, 'T', 'G', '12d_C', '1G', 'DELETERIOUS', 1],
            [17, 7578439, 'T', 'G', '12d_C', '1T', 'DELETERIOUS', 1],
            [17, 7578439, 'T', 'G', '48hr_C', '2', 'DELETERIOUS', 1],
            [17, 7578439, 'T', 'G', '48hr_C', '3only', 'DELETERIOUS', 1],
        ]
        headers = ['chr', 'pos', 'ref', 'alt', 'sample', 'oligo', 'mutation', 'count']
        expected_data = dict(zip(headers, zip(*rows)))
        expected_df = pd.DataFrame(expected_data)

        df = pd.read_csv(os.path.join(temp_dir, 'output.tsv'), header=0, sep='\t')
        self.assertTrue(expected_df.equals(df))

    def test_group_by_oligo_only(self):

        os.system('~/envs/py3.6/bin/python3 ~/Coding/tp53/counts.py -d {} -o {} --groupby oligo'.format(
            temp_dir, os.path.join(temp_dir, 'output.tsv')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'output.tsv')))

        rows = [
            [17, 7578424, 'A', 'C', '1G', 4],
            [17, 7578424, 'A', 'C', '1T', 8],
            [17, 7578424, 'A', 'C', '2', 4],
            [17, 7578424, 'A', 'C', '3only', 4],
            [17, 7578439, 'T', 'G', '1G', 1],
            [17, 7578439, 'T', 'G', '1T', 2],
            [17, 7578439, 'T', 'G', '2', 1],
            [17, 7578439, 'T', 'G', '3only', 1],
        ]
        headers = ['chr', 'pos', 'ref', 'alt', 'oligo', 'count']
        expected_data = dict(zip(headers, zip(*rows)))
        expected_df = pd.DataFrame(expected_data)

        df = pd.read_csv(os.path.join(temp_dir, 'output.tsv'), header=0, sep='\t')
        self.assertTrue(expected_df.equals(df))

    def tearDown(self):
        shutil.rmtree(temp_dir)



    # The code takes a directory structure
    # ##{hr,d}_final{2 in the case of 12d}/vcfs_##{hr,d}_{A-C}/vcfs_##{hr,d}_{A-C}_oligo{1A,C,T,G;2;3only}/(NON-)DELETERIOUS/mut_id#{1,3}_#{1,3}.txt
    # times are 48hr, 96hr, 6d, 8d, 12d

    # the code outputs a TSV file with the columns:
    # chr, pos, ref, alt, sample (time + letter), oligo {1-3etc}, del/non-del, count of that mutation in all combinations for that timepoint and sample
    # both the full (ungrouped) and squashed (each mutation shown just once with total count)
