# Command usage

Below you can find details about Oudjat command usage.
For now, Oudjat includes two operating modes.

1. Command line
2. Configuration file

## Connectors

The connector commands allow you to interact and query implemented connectors.
Every implemented connector return data in the form of a list of dictionaries. Which you can export.

To use one of oudjat connectors, you can reference it like:

```bash
oudjat connectors.<connector_path> [options]
```

You will find every connector reference in their dedicated command details.

The connectors commands share some operations you can pass as options:

| Option             | Description                                                                               |
| ------------------ | ----------------------------------------------------------------------------------------- |
| -t --target=TARGET | Specify the target of the connector. It can be an webpage or API URL or a server hostname |
| --csv=CSV          | Export the retrieved data as a CSV file                                                   |
| --json=JSON        | Export the retrieved data as a JSON file                                                  |

In a lot of cases, the connector will also require that you provide credentials to perform some form of authentication in order to retrieve data.
You can provide credentials with these options

| Option          | Description                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| -u --username   | The username / login to use for the connection                                                                      |
| -p --password   | The password to use for the connection                                                                              |
| --creds-service | Alternatively, you can provide a service name that will be used to store credentials for that particular connector. |

### CERT - CERTFR

A connector used to parse CERTFR pages.

#### Reference

`connectors.cert.certfr`

#### Usage

```bash
oudjat connectors.cert.certfr [options]
```

#### Options

| Option             | Description                                                       |
| ------------------ | ----------------------------------------------------------------- |
| --feed             | CERTFR RSS feed that can be used to parse multiple pages          |
| --date-filter=DATE | A date to filter the feed and retrieve only pages after this date |

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
