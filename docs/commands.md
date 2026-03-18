# Command usage

Below you can find details about Oudjat command line usage.
For now, Oudjat includes two operating modes.

1. 🐚Command line
2. 📜Configuration file

## 🔌 Connectors

The connector commands allow you to interact and query implemented connectors.
Every implemented connector return data in the form of a list of dictionaries. Which you can filter, print or export.

To use one of oudjat connectors, you can reference it like this:

```bash
oudjat connectors.<connector_path> [options]
```

You will find every connector reference in their dedicated command section.

The connectors commands share some operations you can pass as options:

| Option                 | Description                                                                   |
| ---------------------- | ----------------------------------------------------------------------------- |
| -a --append            | Append to the output file. Useful if you want to append logs in the same file |
| -h --help              | Print the doc string                                                          |
| -v --verbose           | Show more logs                                                                |
| -o --output=LOGFILE    | Specify a file to save the execution logs                                     |
| -S --silent            | Simple output                                                                 |
| -V --version           | Show the program version and exit                                             |
| --csv=CSV              | Save results as a CSV file                                                    |
| --json=JSON            | Save results as a JSON file                                                   |
| --print                | Print the results in the terminal                                             |
| --key-filter=KEYFILTER | Filter the final result keys                                                  |

In a lot of cases, the connector will also require that you provide 🔑credentials to perform some form of authentication in order to retrieve data.
You can provide 🔑credentials with these options

| Option          | Description                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| -u --username   | The username / login to use for the connection                                                                      |
| -p --password   | The password to use for the connection                                                                              |
| --creds-service | Alternatively, you can provide a service name that will be used to store credentials for that particular connector. |

Each connector command options can be retrieved by combining the connector ref with the help option like this:

```bash
oudjat connectors.<ref> -h
oudjat connectors.<ref> --help
```

<u>Exemple:</u>

```bash
oudjat connectors.edr.sentinelone --help
```

### CERT - CERTFR

A connector used to parse CERTFR pages.
It returns CERTFR pages content:

- Title
- Description
- Affected products
- Sources
- Risks
- CVEs

You can optionally fetch data for the CVEs referenced in parsed pages.
This will use CVE connectors for various CVE databases like Nist, CVE.org, and more to retrieve CVSS score and other CVE details.

#### Reference

`connectors.cert.certfr`

#### Usage

| Usage    | Description                                                 |
| -------- | ----------------------------------------------------------- |
| --target | Specify a CERTFR page ref to parse                          |
| --feed   | Automatically retrieve and parse CERTFR pages from RSS feed |

```bash
oudjat connectors.cert.certfr (-t=TARGET | --target=TARGET) [--keywords=KEYWORDS] [--max-cve [--limit=LIMIT]] [options]
oudjat connectors.cert.certfr --feed [--feed-date=FEEDDATE] [--keywords=KEYWORDS] [--max-cve [--limit=LIMIT]] [options]
```

#### Options

| Option               | Description                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| --feed-date=FEEDDATE | A filter to retrieve only RSS feed items that were published after a certain date (YYYY-MM-DD format) |
| --limit=LIMIT        | Define a limit to the number of CVEs resolve when using max-cve option [default: 50]                  |
| --max-cve            | Resolve CVEs data and the highests (most critical) ones                                               |
| --keywords=KEYWORDS  | A list of keywords (comma separated, no space)                                                        |

#### Exemples

```bash
oudjat connectors.cert.certfr -t "https://www.cert.ssi.gouv.fr/alerte/CERTFR-2021-ALE-022/"
oudjat connectors.cert.certfr -t "https://www.cert.ssi.gouv.fr/avis/feed/" --feed --date-filter "2025-12-01"
```

### EDR - Cybereason

A connector to interact with Cybereason API.

#### Reference

`connectors.edr.cybereason`

#### Usage

```bash
oudjat connectors.edr.cybereason [options]
```

#### Options

| Option                | Description                                                   |
| --------------------- | ------------------------------------------------------------- |
| --sensors             | Retrieve sensors from the API                                 |
| --sensors-ids=SENSORS | Ids of sensors an action will be performed on                 |
| --edit_policy         | Edit the policy of specified sensors (by ids)                 |
| --file=FILENAME       | Search for a specific file                                    |
| --sensor-restart      | Restart the specified sensors                                 |
| --sensor-remove-group | Remove specified sensors from the given group                 |
| --sensor-assign-group | Assign a new group to the specified sensors                   |
| --fetch=ENDPOINT      | Run a custom query based on the provided endpoint and payload |
| --payload=PAYLOAD     | Assign a new group to the specified sensors                   |

#### Exemple

```bash
# Search for a test.exe file
oudjat connectors.edr.cybereason --file "test.exe"

# Export sensors into a csv file
oudjat connectors.edr.cybereason --sensors --limit 40000 --csv ./sensors.csv
oudjat connectors.edr.cybereason --sensor-assign-group --sensors-list sensors.txt --payload {"argument": groupId}
```

### EDR - Sentinelone

#### Reference

`connectors.edr.sentinelone`

#### Usage

```bash
oudjat connectors.edr.sentinelone [options]
```

#### Options

| Option                       | Description                                              |
| ---------------------------- | -------------------------------------------------------- |
| --agents                     | Retrieve agents details from the API                     |
| --agents-export              | Export agent details as a CSV built natively on API side |
| --move-agent-site=AGENT_NAME | Change the site of the agent                             |
| --sites                      | Retrieve sites informations                              |

#### Exemple

```bash
# Export agents details into a json file
oudjat connectors.edr.sentinelone --agents --json ./agents.json
```

### Endoflife

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### File

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### LDAP

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### MS - CVRF

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### MS - SCCM

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### Tenable - Security Center

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### Vuln - CVE.org

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### Vuln - Nist

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

### Vuln - Circl

#### Reference

``

#### Usage

```bash
```

#### Options

| Option | Description |
| ------ | ----------- |

#### Exemple

```bash
```

## Data collection / ETL
