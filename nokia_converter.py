"""
Converts the hierarchical configuration of Nokia SR OS equipment into a linear form.
example input:
configure
# System Configuration
    system
        name "TEST"
        contact "test@test.com"
        config-backup 10
        load-balancing
            l4-load-balancing
            lsr-load-balancing lbl-ip-l4-teid
            service-id-lag-hashing
        exit
        management-interface
            yang-modules
                no nokia-combined-modules
                nokia-submodules
            exit
        exit
    exit


example output:
configure => system => name "TEST"
configure => system => contact "test@test.com"
configure => system => config-backup 10
configure => system => load-balancing => l4-load-balancing
configure => system => load-balancing => lsr-load-balancing lbl-ip-l4-teid
configure => system => load-balancing => service-id-lag-hashing
configure => system => management-interface => yang-modules => no nokia-combined-modules
configure => system => management-interface => yang-modules => nokia-submodules
"""


def convert_hierarchical_to_linear(data: str, comment_symbol: str = '#',
                                   level_separator: str = ' => ', add_not_config_line: bool = False,
                                   add_exit_to_output: bool = False) -> str:
    """
    :param data: nokia hierarchical configuration
    :param comment_symbol: skip configuration line startswith with that simbol
    :param level_separator: simbols add between level
    :param add_not_config_line: flag to add lines that are not related to the configuration that were in the incoming text
    :param add_exit_to_output: flag to add "exit" config line to output linear config
    :return: linear configuration
    """
    prefix_lst = []  # stack for save prefix
    line_config_lst = []  # list for save linear config line
    previous_indent = 0
    previous_line = 'configure'
    config_part = False

    for line in data.split('\n'):
        # Skip empty line
        if not line:
            continue
        # Check configuration block start
        if line == 'configure':
            config_part = True
            continue
        # If config block is not start add line as is
        if not config_part and add_not_config_line:
            line_config_lst.append(line)
            continue

        # Start analyze configuration
        if config_part:

            # Count space indent
            current_indent = 0
            for ch in line:
                if ch == ' ':
                    current_indent += 1
                else:
                    break

            # Normalize config line
            line = line.strip()

            # Skip the block annotation
            if line.startswith(comment_symbol):
                continue

            # Add branch name to prefix list
            if current_indent > previous_indent:
                if previous_line:
                    prefix_lst.append(previous_line)

            # If indentation has not changed then the previous line was a leaf of the tree
            elif current_indent == previous_indent:
                if previous_line != 'exit' or add_exit_to_output:
                    line_config_lst.append(level_separator.join(prefix_lst) + level_separator + previous_line)

            # End of block, preview line is a leaf
            elif current_indent < previous_indent or line == 'exit':
                if previous_line != 'exit' or add_exit_to_output:
                    line_config_lst.append(level_separator.join(prefix_lst) + level_separator + previous_line)
                if prefix_lst:
                    prefix_lst.pop()

            # End of configuration
            if line == 'exit all':
                config_part = False
            # Save current line for next iteration
            previous_line = line
            previous_indent = current_indent
            # Memory protection from incorrect config
            if len(prefix_lst) > 10:
                raise Exception('The nesting level is too high')

    return '\n'.join(line_config_lst)


def test():

    with open(r'g:\\nokia_test_config.txt', 'r', encoding='utf-8') as file:
        data = file.read()

    with open(r'g:\\nokia_line_config.txt', 'w', encoding='utf-8') as file:
        result = convert_hierarchical_to_linear(data)
        file.write(result)
        print(result)


if __name__ == '__main__':

    test()
