#!/usr/bin/env python
import os
import sys
import argparse


# TODO: custom flags defaults (e.g. name%def_value)
# TODO: security question if want to overwrite existing file
# TODO: Readme
# TODO: Repo name, description and topics, file-name
# TODO: License
# TODO: Handle if can't read input-file
# TODO: Invoke conda afterwards (and flag to disable)
# TODO: Example Files
# TODO: Specify Python version
# TODO: Find file in parent dir if not in own (so if included as submodule)
# TODO: be able to handle == and != w/o spaces
# TODO: block sections
# TODO: add comments / doc-strings / ...


class FieldParser:

    def __init__(self):
        self._flags = []
        self._vars = {}

    def read_argparse(self, flags_list, var_list):
        self._flags = flags_list
        for attr, val in var_list:
            self._vars[attr] = val

    def evaluate_fields(self, fields):
        if len(fields) == 0:
            raise ValueError('Syntax Error')

        if 'or' in fields:
            idx = fields.index('or')
            left = self.evaluate_fields(fields[:idx])
            right = self.evaluate_fields(fields[idx+1:])
            return left or right
        if 'and' in fields:
            idx = fields.index('and')
            left = self.evaluate_fields(fields[:idx])
            right = self.evaluate_fields(fields[idx+1:])
            return left and right
        if fields[0] == 'not':
            return not self.evaluate_fields(fields[1:])

        if len(fields) == 1:
            return fields[0] in self._flags

        if len(fields) == 3:
            if fields[1] in ['==', '!=', 'startswith', 'endswith', 'contains']:
                if fields[0] == 'platform':
                    left = sys.platform
                else:
                    if not fields[0] in self._vars:
                        raise ValueError('Custom variable \'%s\' not defined' % fields[0])
                    left = self._vars[fields[0]]

                if fields[1] == '==':
                    return left == fields[2]
                elif fields[1] == '!=':
                    return left != fields[2]
                elif fields[1] == 'startswith':
                    return left.startswith(fields[2])
                elif fields[1] == 'endswith':
                    return left.endswith(fields[2])
                elif fields[1] == 'contains':
                    return fields[2] in left

        raise ValueError('Syntax Error')


def main():
    argparser = argparse.ArgumentParser()
    argparser.add_argument('-i', '--input', default='environment.yml.meta',
                           help='specify meta environment input file')
    argparser.add_argument('-o', '--output', default='environment.yml',
                           help='specify environment output file')
    argparser.add_argument('-f', '--flag', type=str, action='append', default=[],
                           help='set custom flag for parsing')
    argparser.add_argument('-v', '--variable', type=str, nargs=2, action='append', default=[],
                           help='define custom variable for parsing')
    args = argparser.parse_args()

    fieldparser = FieldParser()
    fieldparser.read_argparse(args.flag, args.variable)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    meta_file = os.path.join(dir_path, args.input)
    env_file = os.path.join(dir_path, args.output)

    file_buffer = []
    with open(meta_file, 'r') as file_in:
        for cnt, line in enumerate(file_in):
            bracket_start = line.find('[')
            bracket_end = line.find(']')
            if bracket_start != -1 and bracket_end != -1:
                bracket_text = line[bracket_start+1:bracket_end]
                fields = bracket_text.split()
                line = line[:bracket_start] + line[bracket_end+1:]
                try:
                    print_line = fieldparser.evaluate_fields(fields)
                except ValueError as e:
                    sys.stderr.write('Line %d: %s\n' % (cnt+1, e))
                    sys.exit(1)

                if not print_line:
                    continue

            file_buffer.append(line)

    with open(env_file, 'w') as file_out:
        for line in file_buffer:
            file_out.write(line)


if __name__ == '__main__':
    main()
