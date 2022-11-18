import os


def str_file_option_handle(self, string_option, file_option):
  """ Initialize a list option based either on a comma separated string or a file """
  if self.options[file_option]:
    full_path = os.path.join(os.getcwd(), self.options[file_option])

    with open(full_path, encoding="utf-8") as f:
      self.options[string_option] = list(filter(None, f.read().split('\n')))

  else:
    self.options[string_option] = list(filter(None, self.options[string_option].split(",")))