import os
import tempfile
from unittest import TestCase

temp_dir = tempfile.mkdtemp()
test_dir = os.path.dirname(os.path.realpath(__file__))


class MainRunTest(TestCase):

    def test_normal_run(self):
        # Erica supplies a directory on the command-line via the -d flag
        # Erica supplies a output file name via the -o flag

        os.system('python ~/Coding/rna-seq/counts.py -d {} -o {}'.format(temp_dir,
                                                                         os.path.join(temp_dir, 'output.tsv')))
        self.assertTrue(os.path.exists(os.path.join(temp_dir, 'output.tsv')))



    # The code takes a directory structure
    # ##{hr,d}_final{2 in the case of 12d}/vcfs_##{hr,d}_{A-C}/vcfs_##{hr,d}_{A-C}_oligo{1A,C,T,G;2;3only}/(NON-)DELETERIOUS/mut_id#{1,3}_#{1,3}.txt
    # times are 48hr, 96hr, 6d, 8d, 12d

    # the code outputs a TSV file with the columns:
    # chr, pos, ref, alt, sample (time + letter), oligo {1-3etc}, del/non-del, count of that mutation in all combinations for that timepoint and sample
    # both the full (ungrouped) and squashed (each mutation shown just once with total count)
