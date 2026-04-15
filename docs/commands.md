# Command usage

Below you can find details about Oudjat command line usage.
For now, Oudjat includes two operating modes.

1. 🐚Command line
2. 📜Configuration file

## 🔌 Connectors

### Description

The connector commands allow you to interact and query implemented connectors.
Every implemented connector return data in the form of a list of dictionaries. Which you can

- filter
- print
- export.

### Basic usage

To use one of oudjat connectors, you can reference it like this:

```bash
oudjat connectors.<connector_path> [options]
```

You will find every connector reference in their **dedicated command section**.

### Options

Oudjat uses [docotp](http://docopt.org/) to handle its usages and command options.

> [!IMPORTANT]
> The most important rule of docopt you need to know is:
> options wrapped with **parenthesis** () or not wrapped at all, are required.
> options wrappped with **brackets** [] are optional.

The connectors commands **share some common operations** you can pass as options:

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
| --sort=SORTKEY         | Sort the final results using the provided key                                 |
| --sort-reverse         | Reverse the sorting order                                                     |

### Credentials

In a lot of cases, the connector will also require that you provide 🔑**credentials** to perform some form of 👤**authentication**.
You can provide 🔑 with these options

| Option          | Description                                                                                                         |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| -u --username   | The username / login to use for the connection                                                                      |
| -p --password   | The password to use for the connection                                                                              |
| --creds-service | Alternatively, you can provide a service name that will be used to store credentials for that particular connector. |

While using the _--creds-service_ option, you can either:

- Provide a username to specifically connect with a certain user
- Provide no extra information. Oudjat will automatically retrieve ailable 🔑 for the specified service

When you specify a credential service name:

1. Oudjat will ask you for a username and password.

```bash
> oudjat connectors.ldap -t "server.domain.local" --creds-service "MyLDAPSrvConnection" ...
> Username for MyLDAPSrvConnection: <my_user>
> Password for MyLDAPSrvConnection: ************
```

2. It will then store the prompted 🔑 in the available credential store on your system:
   - 🐧**Linux**: KWallet, Gnome keyring, etc.
   - 🪟**Windows**: Windows Credential Store

The next time you use the same service, Oudjat will automatically retrieve the registered 🔑 for that service.

> [!Important]
> If multiple username/password pairs are registered for the same service. Oudjat will retrieve the last registered one.
> You can specify the username you want to retrieve credentials for.

So the credentials options are usually handled with the following docopt logic:
`(--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])`

### Help

Each connector command options can be retrieved by combining the connector ref with the help option like this:

```bash
oudjat connectors.<ref> -h
oudjat connectors.<ref> --help
```

<u>Exemple:</u>

```bash
oudjat connectors.edr.sentinelone --help
```

---

## 🔌Connectors - 🌐CERT.CERTFR

### Description

A connector used to parse [CERTFR pages](https://www.cert.ssi.gouv.fr/) .
It returns CERTFR pages content:

- Title
- Description
- Affected products
- Sources
- Risks
- CVEs

### Reference

`connectors.cert.certfr`

### Prerequisites

- No API key, nor special access is required.
- You just need an internet access.

### Usage

| Usage    | Description                                                 |
| -------- | ----------------------------------------------------------- |
| --target | Specify a CERTFR page ref to parse                          |
| --feed   | Automatically retrieve and parse CERTFR pages from RSS feed |

```bash
oudjat connectors.cert.certfr (-t=TARGET | --target=TARGET)
                              [--keywords=KEYWORDS]
                              [--max-cve [--limit=LIMIT]]
                              [options]
oudjat connectors.cert.certfr --feed
                              [--feed-date=FEEDDATE]
                              [--keywords=KEYWORDS]
                              [--max-cve [--limit=LIMIT]]
                              [options]
```

### Options

| Option               | Description                                                                                           |
| -------------------- | ----------------------------------------------------------------------------------------------------- |
| --feed-date=FEEDDATE | A filter to retrieve only RSS feed items that were published after a certain date (YYYY-MM-DD format) |
| --limit=LIMIT        | Define a limit to the number of CVEs resolve when using max-cve option [default: 50]                  |
| --max-cve            | Resolve CVEs data and the highests (most critical) ones                                               |
| --keywords=KEYWORDS  | A list of keywords (comma separated, no space)                                                        |

> [!NOTE]
> You can optionally fetch data for the CVEs referenced in parsed pages using the _--max-cve_ option.
> This will use CVE connectors for various CVE databases like Nist, CVE.org, and more to retrieve CVSS score and other CVE details.

> [!WARNING]
> Since CERTFR pages tend to have a lot of CVE references, you can limit how many are resolved with the _--limit_ option.

### Exemples

```bash
oudjat connectors.cert.certfr -t CERTFR-2021-ALE-022" --max-cve --limit 20
oudjat connectors.cert.certfr --feed --date-filter "2025-12-01"
```

## 🔌 Connectors - EDR.Cybereason

> [!WARNING]
> Cybereason connector is no longer maintained

## 🔌 Connectors - EDR.Sentinelone

### Description

A connector to interact with [SentinelOne](https://www.sentinelone.com/fr/) EDR API.
It provides ability to do various actions:

- Retrieve data (agents, appliations, policies, groups, sites, threats, etc.)
- Move objects (agent to group, group to site)
- Update policies (group, site)
- Update threats status and verdict

### Reference

`connectors.edr.sentinelone`

### Prerequisites

You will need several elements to use this connector:

1. An account on SentinelOne console at least.
2. An API token
3. The required permissions to query the endpoints you want to reach

🔑Credentials are needed for this connector. See [[commands#Credentials]] section.

> [!IMPORTANT]
> For this connector, the password is the API token

### Usage

> [!WARNING]
> Some commands (usages) bellow can have a significant impact on your asssets
> Whether, you want to change a policy, move an asset, change a threat status, etc. It can have direct or indirect consequences
> Trade with the usages marked with ❗ carefully !

| Usage                     | Description                                                                       |
| ------------------------- | --------------------------------------------------------------------------------- |
| --agents                  | Export S1 agents details                                                          |
| --agents-export           | Export flat agent data                                                            |
| --move-agent-site         | ❗Move one or multiple agents to a site based on its id                           |
| --threats                 | Retrieve threats detected by S1                                                   |
| --threats-verdict         | ❗Change the verdict of filtered threats                                          |
| --threats-incident        | ❗Change the verdict and status of filtered threats                               |
| --alert-verdict           | ❗Change the verdict of filtered alerts                                           |
| --alert-incident          | ❗Change the status of filtered alerts                                            |
| --applications            | Retrieve an inventory of applications detected by S1                              |
| --applications-endpoints  | Retrieve an inventory of endpoints for a specific application                     |
| --applications-with-risks | Retrieve an inventory of applications detected by S1 that present a security risk |
| --applications-cves       | Retrieve CVEs for specific application(s)                                         |
| --cves                    | Retrieve CVEs detected by S1                                                      |
| --groups                  | Retrieve groups                                                                   |
| --group-policy            | Retrieve the policy of a specific group                                           |
| --group-policy-update     | ❗Update the policy of the specified groups                                       |
| --group-move-agent        | ❗Move agents into specified group                                                |
| --sites                   | Retrieve sites                                                                    |
| --sites-by-name           | Retrieve sites by names                                                           |

❗: Usage that can impact your environment. Use carefully

```bash
oudjat connectors.edr.sentinelone --agents
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --agents-export
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --move-agent-site
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--sites-list=SITES]
                                  [--names=NAMES]
                                  [options]
oudjat connectors.edr.sentinelone --threats
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --threats-verdict
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--verdict=VERDICT]
                                  [--ids=IDS]
                                  [--sites-list=SITES]
                                  [--status-filter=STATUSFILTER]
                                  [--verdict-filter=VERDICTFILTER]
                                  [--path=PATH]
                                  [--filter=FILTER]
                                  [options]
oudjat connectors.edr.sentinelone --threats-incident
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  (--status=STATUS --verdict=VERDICT)
                                  [--ids=IDS]
                                  [--sites-list=SITES]
                                  [--status-filter=STATUSFILTER]
                                  [--verdict-filter=VERDICTFILTER]
                                  [--path=PATH]
                                  [--auto]
                                  [--filter=FILTER]
                                  [options]
oudjat connectors.edr.sentinelone --alert-verdict
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--verdict=VERDICT]
                                  [--ids=IDS]
                                  [--sites-list=SITES]
                                  [--status-filter=STATUSFILTER]
                                  [--verdict-filter=VERDICTFILTER]
                                  [--path=PATH]
                                  [--filter=FILTER]
                                  [options]
oudjat connectors.edr.sentinelone --alert-incident
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--status=STATUS]
                                  [--ids=IDS]
                                  [--sites-list=SITES]
                                  [--status-filter=STATUSFILTER]
                                  [--verdict-filter=VERDICTFILTER]
                                  [--path=PATH]
                                  [--auto]
                                  [--filter=FILTER]
                                  [options]
oudjat connectors.edr.sentinelone --applications
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--names=NAMES]
                                  [--vendors=VENDOR]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --applications-endpoints
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--names=NAMES]
                                  [--vendors=VENDOR]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --applications-with-risks
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--vendors=VENDOR]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --applications-cves
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--ids=IDS]
                                  [--names=NAMES]
                                  [--vendors=VENDORS]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --cves
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--ids=IDS]
                                  [--severities=SEVERITIES]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --groups
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--names=NAMES]
                                  [--sites-list=SITES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --group-policy
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--ids=IDS]
                                  [options]
oudjat connectors.edr.sentinelone --group-policy-update
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--ids=IDS]
                                  [--malicious-policy=MALPOLICY]
                                  [--suspicious-policy=SUPOLICY]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --group-move-agent
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--ids=IDS]
                                  [--names=NAMES]
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --sites
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--payload=PAYLOAD]
                                  [options]
oudjat connectors.edr.sentinelone --sites-by-name
                                  (-t=TARGET | --target=TARGET)
                                  (--username=USER --password=PASS | --creds-service=SERVICE [--username=USER])
                                  [--names=NAMES]
                                  [--payload=PAYLOAD]
                                  [options]
```

### Options

| Option                                  | Description                                                                |
| --------------------------------------- | -------------------------------------------------------------------------- |
| --auto                                  | Trigger auto mode. See the doc for full usage details                      |
| --auto-mitigation-action=AUTOMITIGATION | Specify the automatic mitigation action                                    |
| --filter=FILTER                         | Provide a JSON filter to narrow down selection                             |
| --ids=IDS                               | A list of IDs to narrow down selection. See the doc for full usage details |
| --malicious-policy=MALPOLICY            | Specify the malicious policy for a group or agent                          |
| --names=NAMES                           | A list of names to narrow down selection                                   |
| --path=PATH                             | A path of a file or process to narrow down selection                       |
| --payload=PAYLOAD                       | A JSON payload to pass additional query parameters                         |
| --severities=SEVERITIES                 | A list severity numbers                                                    |
| --sites-list=SITES                      | A list of site IDs or names                                                |
| --status=STATUS                         | Specify an incident status to an alert or a threat                         |
| --status-filter=STATUSFILTER            | A list of incident statuses for alert/threat selection                     |
| --suspicious-policy=SUPOLICY            | Specify the suspicious policy for a group or agent                         |
| --vendors=VENDORS                       | A list of application vendor for CVEs/application selection                |
| --verdict=VERDICT                       | Specify an incident analyst verdict to an alert or a threat                |
| --verdict-filter=VERDICTFILTER          | a list of incident statuses for alert/threat selection                     |

### Exemple

```bash
# Export agents details into a json file
oudjat connectors.edr.sentinelone -t "myurl.sentinelone.net" --creds-service "S1API" --agents --json ./agents.json

# Change the policy of one or multiple groups
oudjat connectors.edr.sentinelone -t "myurl.sentinelone.net" --creds-service "S1API" --group-policy-update --ids "@./group_ids.txt" --malicious-policy protect
```

## 🔌 Connectors - 🌐Endoflife

### Description

A connector to retrieve data from [endoflife](https://endoflife.date/) API.
Endoflife.date is a website that documents end of life and support lifecycles for various products.

- Applications
- Databases
- Devices
- Frameworks
- Operating Systems
- Server Applications
- Services
- Standards

### Reference

`connectors.endoflife`

### Usage

| Usage              | Description                                 |
| ------------------ | ------------------------------------------- |
| --products         | Retrieve all or a specific product from EOL |
| --product-releases | Retrieve a product release from EOL         |
| --linux            | Retrieve linux related products             |
| --windows          | Retrieve windows related products           |
| --windows-server   | Retrieve windows server related products    |
| --categories       | Retrieve product categories                 |
| --apps             | Retrieve app category products              |
| --oses             | Retrieve os category products               |
| --tags             | Retrieve all, or a specific tag             |

```bash
oudjat connectors.endoflife --products [--product-name=PRODUCTNAME] [--tag=TAG]... [--full] [options]
oudjat connectors.endoflife --product-releases [--product-name=PRODUCTNAME] [--release-name=RELNAME] [options]
oudjat connectors.endoflife --linux [--full] [options]
oudjat connectors.endoflife --windows [options]
oudjat connectors.endoflife --windows-server [options]
oudjat connectors.endoflife --categories [--category-name=CTGNAME] [options]
oudjat connectors.endoflife --apps [options]
oudjat connectors.endoflife --oses [options]
oudjat connectors.endoflife --tags [--tag=TAG] [options]
```

### Options

| Option                     | Description                              |
| -------------------------- | ---------------------------------------- |
| --category-name=CTGNAME    | Specify a product category name          |
| --full                     | If specified, retrieve full product data |
| --product-name=PRODUCTNAME | Specify a product name                   |
| --release-name=RELNAME     | Specify a release name (its version)     |
| --tag=TAG                  | Specify one or several tag (repeatable)  |

### Exemple

```bash
oudjat connectors.endoflife --products --product-name LibreOffice --json ./libreoffice.json
oudjat connectors.endoflife --windows --csv ./windows.csv
```

## 🔌 Connectors - LDAP

### Description

### Reference

`connectors.ldap`

### Usage

```bash
```

### Options

| Option | Description |
| ------ | ----------- |

### Exemple

```bash
```

## 🔌 Connectors - 🌐MS.CVRF

### Reference

`connectors.ms.cvrf`

### Usage

```bash
```

### Options

| Option | Description |
| ------ | ----------- |

### Exemple

```bash
```

## 🔌 Connectors - MS.SCCM

### Reference

`connectors.ms.sccm`

### Usage

```bash
```

### Options

| Option | Description |
| ------ | ----------- |

### Exemple

```bash
```

## 🔌 Connectors - Tenable.SC

### Reference

``

### Usage

```bash
```

### Options

| Option | Description |
| ------ | ----------- |

### Exemple

```bash
```

## 🔌 Connectors - 🌐Vulns

### Reference

``

### Usage

```bash
```

### Options

| Option | Description |
| ------ | ----------- |

### Exemple

```bash
```
