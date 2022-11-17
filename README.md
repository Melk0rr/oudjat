# Oudjat

```
 .                           :-=++**######*+=-:
  -++-.              .:=+*%@@%#*+=--:::::--=+*%@@#+-
     -+##%###*###%%@@%#+=-:                     .-+#@%+-.
           ..:::..            .:-=+**###**+=-.       -*@@@%*+=-
 :                      :-+*##*=-:-@@@@@@@@@@*##*=:     .-+#%@%+
  =**=-::.....::-=+*#%%#*=:       #@@@@@@@@@@:  .-+##+-
     .-=+**###%%%@@@@#+-.         -@@@@@@@@@*        :+%%*=-.
                    .:-+#@#*=:.     -+***+-.  .-=+*%%#**++**#%.
                          .-=*#%@%###***##%%@@@@@%-
        .:-:.                     ...::.-%@@-@@@#      .d88888b.                888  d8b          888
     .*@%*=+*@#:                      .*@@+  %@@+     d88P" "Y88b               888  Y8P          888
    .@@*      @@                    :*@@+    %@@@+    888     888               888               888
    :@@=  .#*#@=                 .=%@%=      @@@@@@-  888     888 888  888  .d88888 8888  8888b.  888888
     *@@-   ..                :+%@%+:       .@@@#=:   888     888 888  888 d88" 888 "888     "88b 888
      -#@@*-.           .:=*%@@#=.          +@*.      888     888 888  888 888  888  888 .d888888 888
        .=*%@@%##**##%%@@%*+-.              @=        Y88b. .d88P Y88b 888 Y88b 888  888 888  888 Y88b.
             ..:----::.                    =+          "Y88888P"   "Y88888  "Y88888  888 "Y888888  "Y888
                                                                                     888
                                                                                    d88P
                                                                                  888P"
```
## Getting Started

### Prerequisites

### Installing

Please note that Oudjat is in alpha

```
git clone https://github.com/Melk0rr/Oudjat.git
cd Oudjat
pip3 install  -r requirements.txt
pip3 install .
```

## Usage

      Usage:
        oudjat (-t TARGET | -f FILE) [-o FILENAME] [-oSv] [-m MODE] [--export-csv CSV] [(--keywords KEYWORDS | --keywordfile KEYWORDFILE)]
        oudjat -h
        oudjat (--version | -V)

      Options:
        -h --help                       show this help message and exit
        -t --target                     set target (comma separated, no spaces, if multiple)
        -f --file                       set target (reads from file, one domain per line)
        -m --mode MODE                  define the mode to use
        -o --output                     save to filename
        -S --silent                     simple output, one per line
        -v --verbose                    print debug info and full request output
        -V --version                    show version and exit
        --export-csv CSV                save results as csv
        --keywords KEYWORDS             set keywords to track (comma separated, no spaces, if multiple)
        --keywordfile KEYWORDFILE       set keywords to track (reads from file, one keyword per line)

      Help:
        For help using this tool, please open an issue on the Github repository:
        https://github.com/Melk0rr/Oudjat

## License