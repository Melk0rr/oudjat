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
        oudjat cert (-t TARGET | -f FILE) [options] [--keywords=KEYWORDS | --keywordfile=KEYWORDFILE]
        oudjat cve (-t TARGET | -f FILE) [options]
        oudjat -h | --help
        oudjat -V | --version

      Commands
        cert                            parse data from cert page
        cve                             parse CVE data from Nist page

      Options:
        -h --help                       show this help message and exit
        -t --target                     set target (comma separated, no spaces, if multiple)
        -f --file                       set target (reads from file, one domain per line)
        -o --output                     save to filename
        -S --silent                     simple output, one per line
        -v --verbose                    print debug info and full request output
        -V --version                    show version and exit
        --check-max-cve                 determine which CVE is the most severe based on the CVSS score
        --export-csv=CSV                save results as csv
        --feed                          run cert mode from a feed
        --filter=FILTER                 date filter to apply with feed option (e.g. 2023-03-10)
        --keywords=KEYWORDS             set keywords to track (comma separated, no spaces, if multiple)
        --keywordfile=KEYWORDFILE       set keywords to track (file, one keyword per line)

      Exemples:
        oudjat cert -t https://cert.ssi.gouv.fr/alerte/feed/ --feed --filter "2023-03-13" --check-max-cve
        oudjat cert -f ./tests/certfr.txt --export-csv ./tests/certfr_20230315.csv --keywordfile ./tests/keywords.txt --check-max-cve
        oudjat cve -f ./tests/cve.txt --export-csv ./tests/cve_20230313.csv

      Help:
        For help using this tool, please open an issue on the Github repository:
        https://github.com/Melk0rr/Oudjat

## License