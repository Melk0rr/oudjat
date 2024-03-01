class ColorPrint:
  RED = '\033[91m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  BLUE = '\033[94m'
  PURPLE = '\033[95m'
  END = '\033[0m'

  @classmethod
  def white(self, s, **kwargs):
    print(s, **kwargs)

  @classmethod
  def red(self, s, **kwargs):
    print(self.RED + s + self.END, **kwargs)

  @classmethod
  def green(self, s, **kwargs):
    print(self.GREEN + s + self.END, **kwargs)

  @classmethod
  def yellow(self, s, **kwargs):
    print(self.YELLOW + s + self.END, **kwargs)

  @classmethod
  def blue(self, s, **kwargs):
    print(self.BLUE + s + self.END, **kwargs)

  @classmethod
  def purple(self, s, **kwargs):
    print(self.PURPLE + s + self.END, **kwargs)

