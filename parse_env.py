#!/usr/bin/env python
import os
import sys
import argparse


# TODO: Handle if can't read input-file
# TODO: Invoke conda afterwards (and flag to disable)
# TODO: Find file in parent dir if not in own (so if included as submodule)
# TODO: infile-path not nec. relative to scrip, outfile-path dep on infile-path (?)
# TODO: be able to handle == and != w/o spaces
# TODO: block sections

# TODO: Example Files
# TODO: Specify Python version
# TODO: add comments / doc-strings / ...
# TODO: Readme
# TODO: Repo name, description and topics, file-name
# TODO: License


class ConditionParser:

    def __init__(self):
        self._flags = []
        self._vars = {}

    def read_argparse(self, flags_list, var_list):
        self._flags = flags_list
        for attr, val in var_list:
            self._vars[attr] = val

    def eval_condition(self, condition):
        fields = condition.split()
        return self._eval_fields(fields)

    def _eval_fields(self, fields):
        if 'or' in fields:
            idx = fields.index('or')
            left = self._eval_fields(fields[:idx])
            right = self._eval_fields(fields[idx + 1:])
            return left or right
        if 'and' in fields:
            idx = fields.index('and')
            left = self._eval_fields(fields[:idx])
            right = self._eval_fields(fields[idx + 1:])
            return left and right
        if len(fields) > 0 and fields[0] == 'not':
            return not self._eval_fields(fields[1:])

        if len(fields) == 1:
            return self._eval_flag(fields[0])

        if len(fields) == 3:
            if fields[1] in ['==', '!=', 'startswith', 'endswith', 'contains']:
                left = self._eval_expression(fields[0])
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

    def _eval_flag(self, name):
        if '%' in name:
            raise ValueError('Flags can\'t have default values')
        else:
            return name in self._flags

    def _eval_expression(self, name):
        if name == 'platform':
            return sys.platform
        else:
            return self._eval_var(name)

    def _eval_var(self, name):
        name_cleaned = name.split('%')[0]
        if name_cleaned not in self._vars:
            if '%' in name:
                return name.split('%')[1]
            else:
                raise ValueError('Custom variable \'%s\' not defined' % name)
        else:
            return self._vars[name_cleaned]


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
    argparser.add_argument('-q', '--quiet', action='store_true',
                           help='quietly overwrite output if already exists')
    args = argparser.parse_args()

    conditionparser = ConditionParser()
    conditionparser.read_argparse(args.flag, args.variable)

    dir_path = os.path.dirname(os.path.realpath(__file__))
    meta_file = os.path.join(dir_path, args.input)
    env_file = os.path.join(dir_path, args.output)

    if os.path.exists(env_file) and not args.quiet:
        input_query = 'Output file already exists, overwrite? [Y]'
        while True:
            answer = input(input_query)
            if answer in ['', 'Y', 'y', 'yes', 'Yes', 'YES']:
                print('YEEES')
                break
            elif answer in ['N', 'n', 'no', 'No', 'NO']:
                print('NOOOO')
                return
            input_query = 'Invalid answer, please answer yes or no: [Y]'

    file_buffer = []
    with open(meta_file, 'r') as file_in:
        for cnt, line in enumerate(file_in):
            bracket_start = line.find('[')
            bracket_end = line.find(']')
            if bracket_start != -1 and bracket_end != -1:
                condition = line[bracket_start+1:bracket_end]
                line = line[:bracket_start] + line[bracket_end+1:]
                try:
                    if not conditionparser.eval_condition(condition):
                        continue
                except ValueError as e:
                    sys.stderr.write('Line %d: %s\n' % (cnt+1, e))
                    sys.exit(1)

            file_buffer.append(line)

    with open(env_file, 'w') as file_out:
        for line in file_buffer:
            file_out.write(line)


if __name__ == '__main__':
    main()
