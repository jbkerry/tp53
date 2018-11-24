import os
import re


class TopLevelDirectory:

    vcf_string = 'vcfs_\d{1,2}(hr|d)_[A-C]'
    first_level_regex = re.compile('\d{1,2}(hr|d)_final(2)?')
    second_level_regex = re.compile(vcf_string)
    third_level_regex = re.compile(vcf_string + '_oligo(1A|1C|1G|1T|2|3only)')
    mutation_file_regex = re.compile('mut_id\d+_\d+\.txt')

    def __init__(self, path):
        self.path = path

    @property
    def first_level_subdirectories(self):
        """Given a top-level directory, will return a list of directories with the timepoint_final structure"""
        dir_contents = os.listdir(self.path)

        return [os.path.join(self.path, subdir) for subdir in
                filter(lambda x: self.first_level_regex.fullmatch(x), dir_contents)]

    @property
    def second_level_subdirectories(self):
        """doc string"""
        wanted_dirs = []
        for subdir in self.first_level_subdirectories:
            subdir_contents = os.listdir(subdir)
            wanted_dirs.extend([os.path.join(subdir, other_dir) for other_dir in
                                filter(lambda x: self.second_level_regex.fullmatch(x), subdir_contents)])

        return wanted_dirs

    @property
    def third_level_subdirectories(self):
        wanted_dirs = []
        for second_level_subdir in self.second_level_subdirectories:
            subdir_contents = os.listdir(second_level_subdir)
            wanted_dirs.extend([os.path.join(second_level_subdir, third_dir) for third_dir in
                                filter(lambda x: self.third_level_regex.fullmatch(x), subdir_contents)])

        return wanted_dirs

    @property
    def mutation_subdirectories(self):
        mutation_subdirs = [os.path.join(third_level_subdir, mutation) for third_level_subdir in
                            self.third_level_subdirectories for mutation in ('DELETERIOUS', 'NON-DELETERIOUS')
                            if os.path.exists(os.path.join(third_level_subdir, mutation))]

        return mutation_subdirs

    @property
    def mutation_files(self):
        wanted_files = []
        for mutation_dir in self.mutation_subdirectories:
            dir_contents = os.listdir(mutation_dir)
            wanted_files.extend([os.path.join(mutation_dir, file) for file in
                                 filter(lambda x: self.mutation_file_regex.fullmatch(x), dir_contents)])

        return wanted_files

