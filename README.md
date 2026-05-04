# Oudjat

```txt
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

## What is it ?

Oudjat is a SOC toolbox and maybe more if I have the time.
It provides an entry point to data sources. While also giving the means to consolidate data into common notions like:

- Users
- Computers
- Softwares
- Risks
- etc.

## Getting Started

### Prerequisites

- python3
- beautifulsoup4
- docopt
- keyring
- ldap3
- lxml
- orjson
- pycryptodome
- pytenable
- requests
- tqdm
- yaspin

### Installing

> [!caution]
> Please note that Oudjat is in **alpha**

1. Clone the repo

```bash
git clone https://codeberg.org/me1k0r/oudjat.git
cd oudjat
```

2. Install the package

- Using _pip_

```bash
pip install .
```

- Using _uv_

```bash
uv tool install .
```

## Usage

    Oudjat

    Oudjat is a SOC toolbox that provides an entry point to various data sources.
    It also allows for complex data consolidation and mapping through a config file system.

    Commands:
        connectors.edr.sentinelone    A command to interact with SentinelOne API through oudjat S1Connector
        connectors.endoflife          A command to interact with endoflife.date API through the oudjat EndOfLifeConnector
        connectors.cert.certfr        A command to parse CERTFR pages through oudjat CERTFRConnector
        connectors.ldap               A command to interact with an LDAP server through the oudjat LDAPConnector
        connectors.tenable.sc         A command to interact with Tenable.sc API through the oudjat TenableSCConnector
        connectors.vulns              A command to interact with some vulnerability databases (CVE.org, Nist, Circl)

    Usage:
        oudjat -h | --help
        oudjat -V | --version

    Options:
        -a --append               Append to the output fileappend to the output file 
        -h --help                 Print the doc string 
        -l --log=LOGGING          Specify the logging level [default: INFO]
        -o --output=LOGFILE       Specify a file to save the execution logs to 
        -S --silent               Simple output 
        -V --version              Show the program version and exit 
        --csv=CSV                 Save results as a CSV file 
        --json=JSON               Save results as a JSON file 
        --print                   Print the results in the terminal 
        --key-filter=KEYFILTER    Filter the final result keys 

    Help:
    For help using this tool, please open an issue on the Codeberg repository:
    https://codeberg.org/me1k0r/oudjat

### Advanced usage

Oudjat currently has 2 operating modes:

1. [Command line](./docs/commands.md)
1. [Configuration file](./docs/config_file.md)

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details
