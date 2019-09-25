#!/usr/bin/env python
import os
import sys
import string


# TODO: parsing (find out if [] used in env-files)
# TODO: platform option
# TODO: comparators
# TODO: many more options
# TODO: custom flags (maybe ask for it if not given, but can also give via cmd line)
# TODO: change input and output
# TODO: sequrity question if want to overwrite existing file
# TODO: Readme
# TODO: Repo name and description, file-name
# TODO: License


def evaluate_bracket(bracket_text):
    bracket_text = bracket_text.translate({ord(c): None for c in string.whitespace})
    if bracket_text.startswith('platform=='):
        return bracket_text[10:] == sys.platform
    return None


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
                line = line[:bracket_start] + line[bracket_end+1:]
                print_line = evaluate_bracket(bracket_text)
                if print_line is None:
                    sys.stderr.write('Error: Could not parse bracket in line %d\n' % (cnt+1))
                    sys.exit(1)
                if not print_line:
                    continue
            file_buffer.append(line)

    with open(env_file, 'w') as file_out:
        for line in file_buffer:
            file_out.write(line)


if __name__ == '__main__':
    main()
