from unittest import TestCase
from unittest.mock import patch

from pandas import DataFrame

from core.utils.mutation_counters import convert_mutation_file_to_dataframe, os

test_dir = os.path.dirname(os.path.realpath(__file__))
resource_dir = os.path.join(test_dir, 'resources')


class DataframeTest(TestCase):

    @patch('os.path.split')
    def test_converts_to_desired_dataframe(self, mocked_split):
        expected_data = {
            'chr': ['17'],
            'pos': ['7578424'],
            'ref': ['A'],
            'alt': ['C'],
            'sample': ['48hr_C'],
            'oligo': ['1A'],
            'mutation': ['DELETERIOUS'],
            'count': [3]
        }

        test_file = os.path.join(resource_dir, 'mut_id8_3.txt')
        expected_df = DataFrame(expected_data)

        mocked_split.return_value = ('/my/fake/dir/48hr_final/vcfs_48hr_C/vcfs_48hr_C_oligo1A/DELETERIOUS',
                                     'mut_id8_3.txt')
        df = convert_mutation_file_to_dataframe(test_file)
        self.assertTrue(expected_df.equals(df))
        mocked_split.assert_called_once()


