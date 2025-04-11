"""Handle list init based on given text file or comma separated strings"""

import os


def str_file_option_handle(self, string_option: str, file_option: str) -> None:
    """
    This function handles the initialization of a list-based option by checking if an existing option is provided as a file path.
    If the `file_option` exists in the `self.options` dictionary, it reads the content of the specified file and splits it into lines,
    filtering out any empty lines to create a list which is then assigned to the `string_option`.

    If the `file_option` does not exist, it assumes that the option is provided as a comma-separated string. It splits this string by commas
    and filters out any empty entries to create a list, which is then assigned to the `string_option`.

    Args:
        self (object)      : The instance of the class containing the options dictionary.
        string_option (str): The key in the `self.options` dictionary where the resulting list should be stored.
        file_option (str)  : The key in the `self.options` dictionary that, if exists, points to a file path.
    """

    if self.options[file_option]:
        full_path = os.path.join(os.getcwd(), self.options[file_option])

        with open(full_path, encoding="utf-8") as f:
            self.options[string_option] = list(filter(None, f.read().split("\n")))

    else:
        self.options[string_option] = list(filter(None, self.options[string_option].split(",")))
