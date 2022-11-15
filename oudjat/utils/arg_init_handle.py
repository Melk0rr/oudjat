import os


def init_args(string_list, file_path):
  """ Initialize argument with provided file content or with string list """
  if file_path:
    full_path = os.path.join(os.getcwd(), file_path)

    with open(full_path, encoding="utf-8") as f:
      string_list = list(filter(None, f.read().split('\n')))

  else:
    string_list = list(filter(None, string_list.split(",")))