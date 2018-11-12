import os
import shutil
import tempfile
from unittest import TestCase

import pandas as pd

temp_dir = tempfile.mkdtemp()
test_dir = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(test_dir, '..', 'tests', 'resources')


class MainRunTest(TestCase):

    def test_normal_run(self):
        # Erica supplies a directory on the command-line via the -d flag
        # Erica supplies a output file name via the -o flag
        common_directory = os.path.join(temp_dir, '48hr_final', 'vcfs_48hr_C', 'vcfs_48hr_C_oligo1A')
        del_directory = os.path.join(common_directory, 'DELETERIOUS')
        non_del_directory = os.path.join(common_directory, 'NON-DELETERIOUS')
        os.makedirs(del_directory)
        os.makedirs(non_del_directory)
        for mut_file in os.listdir(resource_dir):
            shutil.copy(os.path.join(resource_dir, mut_file), del_directory)
        os.system('~/envs/py3.6/bin/python3 ~/Coding/tp53/counts.py -d {} -o {}'.format(
                  temp_dir, os.path.join(temp_dir, 'output.tsv')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'output.tsv')))

        row1 = ['17', 7578424, 'A', 'C', '48hr_C', '1A', 'DELETERIOUS', 4]
        row2 = ['17', 7578439, 'T', 'G', '48hr_C', '1A', 'DELETERIOUS', 1]
        headers = ['chr', 'pos', 'ref', 'alt', 'sample', 'oligo', 'mutation', 'count']
        expected_data = dict(zip(headers, zip(row1, row2)))
        expected_df = pd.DataFrame(expected_data)

        df = pd.read_csv(os.path.join(temp_dir, 'output.tsv'), header=0, sep='\t')
        self.assertTrue(expected_df.equals(df))

        shutil.rmtree(temp_dir)



    # The code takes a directory structure
    # ##{hr,d}_final{2 in the case of 12d}/vcfs_##{hr,d}_{A-C}/vcfs_##{hr,d}_{A-C}_oligo{1A,C,T,G;2;3only}/(NON-)DELETERIOUS/mut_id#{1,3}_#{1,3}.txt
    # times are 48hr, 96hr, 6d, 8d, 12d

    # the code outputs a TSV file with the columns:
    # chr, pos, ref, alt, sample (time + letter), oligo {1-3etc}, del/non-del, count of that mutation in all combinations for that timepoint and sample
    # both the full (ungrouped) and squashed (each mutation shown just once with total count)
