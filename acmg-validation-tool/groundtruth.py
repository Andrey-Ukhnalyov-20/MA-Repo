#!/usr/bin/env python3

import requests
import argparse
import pandas as pd

default_request_url = "https://erepo.clinicalgenome.org/evrepo/api/classifications"

parameters = {
        "matchMode": "exact",
        "matchLimit": "none"
        }


def make_request(request_url: str, parameter_name: str, parameter_value: str) -> dict:
    parameters.update({parameter_name: parameter_value})

    response = requests.get(request_url, params=parameters)
    print(type(response))
    response_transformed = response.json()
    print(type(response_transformed))

    return response_transformed


def save_to_csv(variants_form_database: list) -> None:
    dictionary_for_dataframe = {
            'ClinVar variation ID': [],
            'Gene': [],
            'Expert panel': [],
            'Evidence met': [],
            'Evidence not met': [],
            'Decision': []
            }

    for variant in variants_form_database:
        dictionary_for_dataframe['ClinVar variation ID'].append(variant['variationId'])
        dictionary_for_dataframe['Gene'].append(variant['gene']['label'])
        dictionary_for_dataframe['Expert panel'].append(variant['guidelines'][0]['agents'][0]['affiliation'])
        dictionary_for_dataframe['Decision'].append(variant['guidelines'][0]['outcome']['label'])

        list_of_met = []
        list_of_not_met = []

        for evidence in variant['guidelines'][0]['agents'][0]['evidenceCodes']:
            if evidence['status'] == 'Met':
                list_of_met.append(evidence['label'])
            elif evidence['status'] == 'Not Met':
                list_of_not_met.append(evidence['label'])
        
        dictionary_for_dataframe['Evidence met'].append(' '.join(list_of_met))
        dictionary_for_dataframe['Evidence not met'].append(' '.join(list_of_not_met))

    df = pd.DataFrame.from_dict(dictionary_for_dataframe)
    df.to_csv('groundtruth.csv', sep=';')


def cli_interface() -> tuple[str, str, str]:
    parser = argparse.ArgumentParser(description='List parameter name and parameter value')
    parser.add_argument('--url', type=str, nargs='?', default=default_request_url)
    parser.add_argument('--name', type=str, required=True)
    parser.add_argument('--value', type=str, required=True, nargs='+')
    arguments = parser.parse_args()

    return arguments.url, arguments.name, ' '.join(arguments.value)


def main():
    url, pn, pv = cli_interface()
    json_from_database = make_request(url, pn, pv)
    print(type(json_from_database))
    save_to_csv(json_from_database['variantInterpretations'])


if __name__ == "__main__":
    main()

