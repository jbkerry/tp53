from itertools import chain, compress
import tempfile
from unittest import TestCase
from unittest.mock import patch, PropertyMock, Mock

from core.utils.directory_parsers import TopLevelDirectory, os

temp_dir = tempfile.mkdtemp()
test_dir = os.path.dirname(os.path.realpath(__file__))

dir_name = '/my/fake/directory'
top_level_directory = TopLevelDirectory(dir_name)


@patch('os.listdir')
class TestParsers(TestCase):

    def test_path_attribute(self, mocked_listdir):
        self.assertEqual(dir_name, top_level_directory.path)

    def test_returns_first_level_subdirectories_with_correct_name_format(self, mocked_listdir):
        mocked_listdir.return_value = ['48hr_final', '96hr_final', 'random_directory', '12d_final2']

        expected_directories = [os.path.join(dir_name, subdir) for subdir in ('48hr_final', '96hr_final', '12d_final2')]
        self.assertEqual(expected_directories, top_level_directory.first_level_subdirectories)
        mocked_listdir.assert_called_once()

    @patch('core.utils.directory_parsers.TopLevelDirectory.first_level_subdirectories', new_callable=PropertyMock)
    def test_returns_second_level_subdirectories_with_correct_name_format(
            self, mocked_first_level_subdirectories, mocked_listdir):
        dir_structure = {
            '48hr_final': ('vcfs_48hr_A', 'random_directory', 'not_wanted'),
            '12d_final2': ('vcfs_12d_C', 'file1.txt', 'vcfs_12d_B', 'vcfs_hr_C'),
            '96hr_final': ('vcfs_96hr_B',)
        }

        mocked_first_level_subdirectories.return_value = [os.path.join(dir_name, first_subdir) for first_subdir in
                                                          dir_structure.keys()]
        mocked_listdir.side_effect = dir_structure.values()

        expected_directories = {
            '48hr_final': ('vcfs_48hr_A',),
            '12d_final2': ('vcfs_12d_C', 'vcfs_12d_B'),
            '96hr_final': ('vcfs_96hr_B',)
        }
        expected_directories_flat = []
        for dir, subdirs in expected_directories.items():
            expected_directories_flat.extend([os.path.join(dir_name, dir, subdir) for subdir in subdirs])

        self.assertEqual(expected_directories_flat, top_level_directory.second_level_subdirectories)
        mocked_first_level_subdirectories.assert_called_once()
        self.assertEqual(3, mocked_listdir.call_count)

    @patch('core.utils.directory_parsers.TopLevelDirectory.second_level_subdirectories', new_callable=PropertyMock)
    def test_returns_third_level_subdirectories_with_correct_name_format(
            self, mocked_second_level_subdirectories, mocked_listdir):
        dir_structure = {
            os.path.join('48hr_final', 'vcfs_48hr_A'): ('vcfs_48hr_A_oligo1G', 'vcfs_48hr_A_oligo2', 'myfile.txt'),
            os.path.join('12d_final2', 'vcfs_12d_C'): ('vcfs_12d_C_oligo3only', 'vcfs_12d_C_oligo1A'),
            os.path.join('12d_final2', 'vcfs_12d_B'): ('vcfs_12d_B_oligo1G', 'vcfs_12d_B_oligo1F', 'vcfs_12d_B_oligo3'),
            os.path.join('96hr_final', 'vcfs_96hr_B'): ('vcfs_96hr_B_oligo1C', 'old_vcfs', 'vcfs_96hr_B_oligo2')
        }
        mocked_second_level_subdirectories.return_value = [os.path.join(dir_name, second_subdir) for second_subdir in
                                                           dir_structure.keys()]
        mocked_listdir.side_effect = dir_structure.values()

        expected_directories = {
            os.path.join('48hr_final', 'vcfs_48hr_A'): ('vcfs_48hr_A_oligo1G', 'vcfs_48hr_A_oligo2'),
            os.path.join('12d_final2', 'vcfs_12d_C'): ('vcfs_12d_C_oligo3only', 'vcfs_12d_C_oligo1A'),
            os.path.join('12d_final2', 'vcfs_12d_B'): ('vcfs_12d_B_oligo1G',),
            os.path.join('96hr_final', 'vcfs_96hr_B'): ('vcfs_96hr_B_oligo1C', 'vcfs_96hr_B_oligo2')
        }
        expected_directories_flat = []
        for dir, subdirs in expected_directories.items():
            expected_directories_flat.extend([os.path.join(dir_name, dir, subdir) for subdir in subdirs])

        self.assertEqual(expected_directories_flat, top_level_directory.third_level_subdirectories)
        mocked_second_level_subdirectories.assert_called_once()
        self.assertEqual(4, mocked_listdir.call_count)

    @patch('os.path.exists')
    @patch('core.utils.directory_parsers.TopLevelDirectory.third_level_subdirectories', new_callable=PropertyMock)
    def test_returns_all_deleterious_and_non_deleterious_directories(
            self, mocked_third_level_subdirectories, mocked_path_exists, mocked_listdir):
        third_level_subdirectories = [
            os.path.join(dir_name, '48hr_final', 'vcfs_48hr_A', 'vcfs_48hr_A_oligo1G'),
            os.path.join(dir_name, '48hr_final', 'vcfs_48hr_A', 'vcfs_48hr_A_oligo2'),
            os.path.join(dir_name, '12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo3only'),
            os.path.join(dir_name, '12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1A'),
            os.path.join(dir_name, '12d_final2', 'vcfs_12d_B', 'vcfs_12d_B_oligo1G'),
            os.path.join(dir_name, '96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo1C'),
            os.path.join(dir_name, '96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo2')
        ]
        mocked_third_level_subdirectories.return_value = third_level_subdirectories
        mocked_path_exists.return_value = True
        expected_directories = []
        for third_level_dir in third_level_subdirectories:
            expected_directories.extend([os.path.join(third_level_dir, mut_type) for mut_type in
                                         ('DELETERIOUS', 'NON-DELETERIOUS')])

        self.assertEqual(expected_directories, top_level_directory.mutation_subdirectories)
        mocked_third_level_subdirectories.assert_called_once()

    @patch('os.path.exists')
    @patch('core.utils.directory_parsers.TopLevelDirectory.third_level_subdirectories', new_callable=PropertyMock)
    def test_does_not_return_non_existing_deleterious_directories(
            self, mocked_third_level_subdirectories, mocked_path_exists, mocked_listdir):
        third_level_subdirectories = [
            os.path.join(dir_name, '48hr_final', 'vcfs_48hr_A', 'vcfs_48hr_A_oligo1G'),
            os.path.join(dir_name, '12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo3only'),
            os.path.join(dir_name, '96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo2')
        ]
        mocked_third_level_subdirectories.return_value = third_level_subdirectories

        expected_directories = []
        del_non_del_exists = ((False, True), (False, False), (True, True))
        for dels_exist, third_level_dir in zip(del_non_del_exists, third_level_subdirectories):
            expected_directories.extend(list(compress(
                [os.path.join(third_level_dir, mut_type) for mut_type in ('DELETERIOUS', 'NON-DELETERIOUS')],
                dels_exist
            )))

        mocked_path_exists.side_effect = list(chain(*del_non_del_exists))

        self.assertEqual(expected_directories, top_level_directory.mutation_subdirectories)
        mocked_third_level_subdirectories.assert_called_once()


    @patch('core.utils.directory_parsers.TopLevelDirectory.mutation_subdirectories', new_callable=PropertyMock)
    def test_returns_all_mutation_files(
            self, mocked_mutation_subdirectories, mocked_listdir):
        dir_structure = {
            os.path.join('12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1A', 'DELETERIOUS'):
                ('mut_id2_16.txt', 'mut_id12_8.txt', 'file1.txt', 'nut_id12_8.txt'),
            os.path.join('12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1A', 'NON-DELETERIOUS'):
                ('mut_id1_5.txt',),
            os.path.join('96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo1C', 'DELETERIOUS'):
                ('mut_id19_2.txt', 'mut_id6_1.txt'),
            os.path.join('96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo1C', 'NON-DELETERIOUS'):
                ('mut_id4_5.txt', 'mut_ID4_5.txt', 'mut_id16_3.txt'),
            os.path.join('48hr_final', 'vcfs_48hr_A', 'vcfs_48hr_A_oligo1G', 'DELETERIOUS'):
                ('mut_id3_27.txt', 'mut_id3_ab.txt')
        }

        mocked_mutation_subdirectories.return_value = [os.path.join(dir_name, mutation_subdir) for mutation_subdir in
                                                       dir_structure.keys()]
        mocked_listdir.side_effect = dir_structure.values()

        expected_files = {
            os.path.join('12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1A', 'DELETERIOUS'):
                ('mut_id2_16.txt', 'mut_id12_8.txt'),
            os.path.join('12d_final2', 'vcfs_12d_C', 'vcfs_12d_C_oligo1A', 'NON-DELETERIOUS'):
                ('mut_id1_5.txt',),
            os.path.join('96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo1C', 'DELETERIOUS'):
                ('mut_id19_2.txt', 'mut_id6_1.txt'),
            os.path.join('96hr_final', 'vcfs_96hr_B', 'vcfs_96hr_B_oligo1C', 'NON-DELETERIOUS'):
                ('mut_id4_5.txt', 'mut_id16_3.txt'),
            os.path.join('48hr_final', 'vcfs_48hr_A', 'vcfs_48hr_A_oligo1G', 'DELETERIOUS'):
                ('mut_id3_27.txt',)
        }

        expected_directories_flat = []
        for dir, file_names in expected_files.items():
            expected_directories_flat.extend([os.path.join(dir_name, dir, file_name) for file_name in file_names])

        self.assertEqual(expected_directories_flat, top_level_directory.mutation_files)
        mocked_mutation_subdirectories.assert_called_once()
        self.assertEqual(5, mocked_listdir.call_count)