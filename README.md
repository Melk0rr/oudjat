# Oudjat

```
   .-=*#%@@%%%%%%%%#*+-:                
 *#*+=:.           ..-=*%%*=-.          
                          .-=*#****+++==
     .=*#%%@@%%##*=-:                   
   .*%=-@@@@@@@@@ .:=*#*=:.             
 .+#-   #@@@@@@@*  .:+%#**************#=
-##++*#**%@@@@%#+++=:.                  
     :@@@=+%@@=.                        
     +@@@   .=#@#=.                =-=--
     #@@#       :+#%*-.            =-= *
      %@*           :=*#*=:.         .=-
      -@=                :-+*+++=====:  

    ____          __  _      __ 
   / __ \__ _____/ / (_)__ _/ /_
  / /_/ / // / _  / / / _ `/ __/
  \____/\_,_/\_,_/_/ /\_,_/\__/ 
                |___/           
```
## Getting Started

### Prerequisites
- python3
- setuptools
- docopt
- keyring
- requests

### Installing

> [!caution]
> Please note that Oudjat is in **alpha** 
>

```bash
git clone https://github.com/Melk0rr/Oudjat.git
cd Oudjat
pip3 install  -r requirements.txt
pip3 install .
```

## Usage

      Usage:
        oudjat cert (-t TARGET | -f FILE) [options]  [--feed] [--filter=FILTER]
                                                      [--keywords=KEYWORDS | --keywordfile=FILE]   
        oudjat vuln (-t TARGET | -f FILE) [options]
        oudjat kpi (-d DIRECTORY) [options] [--config=CONFIG] [--history=HIST] [--history-gap=GAP]
        oudjat sc (-t TARGET | -f FILE) (--sc-url=SC_URL) [--sc-mode=SC_MODE]
        oudjat -h | --help
        oudjat -V | --version

      Commands
        cert                            parse data from cert page
        kpi                             generates kpi
        vuln                            parse CVE data from Nist page
        
      Options:
        -c --config=CONFIG              specify config file
        -d --directory                  set target (reads from file, one domain per line)
        -f --file                       set target (reads from file, one domain per line)
        -h --help                       show this help message and exit
        -H --history=HIST               check kpis for last n element
        -l --cve-list=CVE_LIST          provide a list of cve to be used as a database and reduce the amount of requests
        -o --output=FILENAME            save to filename
        -S --silent                     simple output, one per line
        -t --target                     set target (comma separated, no spaces, if multiple)
        -v --verbose                    print debug info and full request output
        -V --version                    show version and exit
        -x --export-csv=CSV             save results as csv
        --history-gap=GAP               gap between elements

      Cert-options:
        --feed                          run cert mode from a feed
        --filter=FILTER                 date filter to apply with feed option (e.g. 2023-03-10)
        --keywords=KEYWORDS             set keywords to track (comma separated, no spaces, if multiple)
        --keywordfile=KEYWORDFILE       set keywords to track (file, one keyword per line)

      Exemples:
        oudjat cert -t https://cert.ssi.gouv.fr/alerte/feed/ --feed --filter "2023-03-13"
        oudjat cert -f ./tests/certfr.txt --export-csv ./tests/certfr_20230315.csv --keywordfile ./tests/keywords.txt
        oudjat vuln -f ./tests/cve.txt --export-csv ./tests/cve_20230313.csv

      Help:
        For help using this tool, please open an issue on the Github repository:
        https://github.com/Melk0rr/Oudjat

## License
This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
