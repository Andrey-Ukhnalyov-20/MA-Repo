#!/usr/bin/env python3

import requests
import json

request_url = "https://erepo.clinicalgenome.org/evrepo/api/classifications"

parameters = {
        "matchMode": "exact",
        "matchLimit": "none"
        }


def make_request(parameter_name: str, parameter_value: str) -> str:
    '''
    INPUT:
    parameter_name: str - name of parameter to request
    parameter_value: str - value of parameter to request

    OUTPUT:
    response_transformed: str - result of "get" request transformed to str
    '''
    parameters.update({parameter_name: parameter_value})

    response = requests.get(request_url, params=parameters)
    response_transformed = json.dumps(response.json(), sort_keys=True, indent=2)

    return response_transformed


def main():
    pn = input("Input parameter name: ")
    pv = input("Input parameter value: ")
    json_from_database = make_request(pn, pv)
    print(json_from_database)


if __name__ == "__main__":
    main()

