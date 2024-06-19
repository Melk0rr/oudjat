class ColorPrint:
  RED = '\033[91m'
  GREEN = '\033[92m'
  YELLOW = '\033[93m'
  BLUE = '\033[94m'
  PURPLE = '\033[95m'
  END = '\033[0m'

  @classmethod
  def white(self, s: str, **kwargs) -> None:
    print(s, **kwargs)

  @classmethod
  def red(self, s: str, **kwargs) -> None:
    print(self.RED + s + self.END, **kwargs)

  @classmethod
  def green(self, s: str, **kwargs) -> None:
    print(self.GREEN + s + self.END, **kwargs)

  @classmethod
  def yellow(self, s: str, **kwargs) -> None:
    print(self.YELLOW + s + self.END, **kwargs)

  @classmethod
  def blue(self, s: str, **kwargs) -> None:
    print(self.BLUE + s + self.END, **kwargs)

  @classmethod
  def purple(self, s: str, **kwargs) -> None:
    print(self.PURPLE + s + self.END, **kwargs)

