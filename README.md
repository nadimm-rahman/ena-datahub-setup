# ena-datahub-setup

## Background
This tool carries out data hub set up at the European Nucleotide Archive (ENA). For more information on the data hubs, see the [COMPARE Data Hubs](https://academic.oup.com/database/article/doi/10.1093/database/baz136/5685390) publication. As part of the set up procedure, a user/data hub coordinator does the following:
- Request an unused data hub.
- Provide their contact details with information on any consortium or institute or intended use of the hub. This includes providing a short and public description for the data hub.
- Define lists of data providers (they should have Webin accounts) and data consumers.
- Requests analysis and visualisation tools to be associated with the data hub.

## Usage

To invoke the tool, use `emailer.py` and provide a completed spreadsheet of data providers and consumers. A template spreadsheet has been included in this repository, which can be adapted. Ensure that you have edited `config.yaml` to include an admin or sender email address.

`python emailer.py -s DH_Providers_Consumers.xlsx -d <DATA HUB NAME> -p <DATA HUB PASSWORD>`