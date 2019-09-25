#!/usr/bin/env python
import os
import sys


# TODO: custom flags (maybe ask for it if not given, but can also give via cmd line)
# TODO: custom flags defaults
# TODO: change input and output
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


def evaluate_fields(fields):
    if len(fields) == 0:
        raise ValueError

    if 'or' in fields:
        idx = fields.index('or')
        left = evaluate_fields(fields[:idx])
        right = evaluate_fields(fields[idx+1:])
        return left or right
    if 'and' in fields:
        idx = fields.index('and')
        left = evaluate_fields(fields[:idx])
        right = evaluate_fields(fields[idx+1:])
        return left and right
    if fields[0] == 'not':
        return not evaluate_fields(fields[1:])

    if len(fields) == 1:
        print('evaluate boolean', fields[0], 'as True')
        return True

    if len(fields) == 3:
        if fields[1] in ['==', '!=', 'startswith', 'endswith', 'contains']:
            if fields[0] == 'platform':
                left = sys.platform
            else:
                print('evaluate string', fields[0], 'as string_content')
                left = 'string_content'
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

    raise ValueError


def main():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    meta_file = os.path.join(dir_path, 'environment.yml.meta')
    env_file = os.path.join(dir_path, 'environment.yml')

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
                    print_line = evaluate_fields(fields)
                except ValueError:
                    sys.stderr.write('Error: Could not parse bracket in line %d\n' % (cnt+1))
                    sys.exit(1)
                print(print_line)
                if not print_line:
                    continue
            file_buffer.append(line)

    with open(env_file, 'w') as file_out:
        for line in file_buffer:
            file_out.write(line)


if __name__ == '__main__':
    main()
