import argparse


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', '-d', type=str, help='directory with file', required=True)
    parser.add_argument('--output', '-o', type=str, help='output file name', required=True)
    args = parser.parse_args()

    with open(args.output, 'w'):
        pass
