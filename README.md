# ena-datahub-setup

## Background
This tool carries out data hub set up at the European Nucleotide Archive (ENA). For more information on the data hubs, see the [COMPARE Data Hubs](https://academic.oup.com/database/article/doi/10.1093/database/baz136/5685390) publication. As part of the set up procedure, a user/data hub coordinator does the following:
- Request an unused data hub.
- Provide their contact details with information on any consortium or institute or intended use of the hub. This includes providing a short and public description for the data hub.
- Define lists of data providers (they should have Webin accounts) and data consumers.
- Requests analysis and visualisation tools to be associated with the data hub.

## Usage
Prior to running scripts, ensure the following have been completed:
1. Complete the spreadsheet for data hub setup. This includes providing information regarding the data hub coordinator, the data hub, and listing data providers and data consumers. A template spreadsheet has been included in the repository `DH_Providers_Consumers.xlsx`.
2. Include configuration information in `config.yaml`, e.g. `ADMIN_EMAIL: my_email@gmail.com`.
3. Once cx_Oracle has been installed, define the folder path at the top of `assigner.py` or save as an environment variable - `ORACLE_CLIENT_LIB`.


To assign a data hub and link Webin account(s) to it, use `assigner.py`, providing a completed spreadsheet, with the unassigned data hub name and credentials.

`python assigner.py -s DH_Providers_Consumers.xlsx -d <DATA HUB NAME> -p <DATA HUB PASSWORD>`

Once a data hub has been assigned, to send emails to a list of providers and consumers, use `emailer.py` and provide a completed spreadsheet of data providers and consumers.

`python emailer.py -s DH_Providers_Consumers.xlsx -d <DATA HUB NAME> -p <DATA HUB PASSWORD>`

## Requirements
To run this tool, there are several requirements:
- cx_Oracle (https://cx-oracle.readthedocs.io/en/latest/user_guide/installation.html)
- Python 3.7+ (https://www.python.org/downloads/)
- Python Pandas (https://pandas.pydata.org/docs/getting_started/install.html)
