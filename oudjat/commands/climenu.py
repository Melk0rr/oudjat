""" Cli Menu command """

class CLIMenu(object):
  """ Cli Menu command """

  def __init__(self, options, *args, **kwargs):
    self.options = []

    for i, option in enumerate(options):
      if [ *option.keys() ] == ["name", "action"]:
        self.options.append(option)
      else:
        raise ValueError(f"Invalid option {i}. All options must be provided a name and an action !")

    self.args = args
    self.kwargs = kwargs

  def run(self):
    """ Run command """
