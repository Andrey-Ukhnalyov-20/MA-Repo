#!/usr/bin/env python3

import argparse
import json
import pandas as pd
import matplotlib.pyplot as plt
import groundtruth

ACMG_criteria_list = []
test_results_list = []

# Dictionarie for criteria validation
# 'criteria': [TP, TN, FP, FN]
ACMG_criteria_validation = dict()


def parse_test_results(test_results: list) -> None:
    for variant in test_results:
        variant_information_list = [
                variant['variationId'],
                variant['gene'],
                [evidence for evidence in variant['evidenceMet']],
                [evidence for evidence in variant['evidenceNotMet']],
                variant['decision']
                ]
        test_results_list.append(variant_information_list)

        for evidence in variant_information_list[2]:
            if evidence not in ACMG_criteria_list:
                ACMG_criteria_list.append(evidence)

        for evidence in variant_information_list[3]:
            if evidence not in ACMG_criteria_list:
                ACMG_criteria_list.append(evidence)


def make_analysis(groungtruth_file: str):
    for variant in test_results_list:
        if groungtruth_file == 'no':
            json_from_database = groundtruth.make_request(
                    groundtruth.default_request_url,
                    'gene',
                    variant[1])
            groundtruth.save_to_csv(json_from_database['variantInterpretations'])

        groundtruth_dataframe = pd.read_csv('groundtruth.csv', sep=';')
        variant_from_groundtruth = groundtruth_dataframe.loc[groundtruth_dataframe['ClinVar variation ID'] == int(variant[0])]
        ACMG_met_from_groundtruth = variant_from_groundtruth.loc[:, 'Evidence met'].to_list()[0].split(' ')
        ACMG_not_met_from_groundtruth = variant_from_groundtruth.loc[:, 'Evidence not met'].to_list()[0].split(' ')
        
        TP = TN = FP = FN = 0
        for criteria in variant[2]:
            if criteria in ACMG_met_from_groundtruth:
                TP = 1
            else: FP = 1

            if criteria not in ACMG_criteria_validation:
                ACMG_criteria_validation.update({criteria: [TP, 0, FP, 0]})
            else:
                ACMG_criteria_validation[criteria][0] += TP
                ACMG_criteria_validation[criteria][2] += FP
        
        for criteria in variant[3]:
            if criteria in ACMG_not_met_from_groundtruth:
                TN = 1
            else: FN = 1

            if criteria not in ACMG_criteria_validation:
                ACMG_criteria_validation.update({criteria: [0, TN, 0, FN]})
            else:
                ACMG_criteria_validation[criteria][1] += TN
                ACMG_criteria_validation[criteria][3] += FN


def make_output(output_type: str, test_id: str) -> None:
    sensitivity = precision = f1_score = accuracy = 0
    for criteria in ACMG_criteria_list:
        initial_parameters = ACMG_criteria_validation[criteria]
        try:
            sensitivity = initial_parameters[0] / (initial_parameters[0] + initial_parameters[3])
        except: sensitivity = 0
        try:
            precision = initial_parameters[0] / (initial_parameters[0] + initial_parameters[2])
        except: precision = 0
        try:
            f1_score = (2 * precision * sensitivity) / (precision + sensitivity)
        except: f1_score = 0
        try:
            accuracy = (initial_parameters[0] + initial_parameters[1]) / sum(initial_parameters)
        except: accuracy = 0

        if output_type == 'cli':
            output_lines = [
                    f'ACMG criteria: {criteria}',
                    f'TP: {initial_parameters[0]}',
                    f'TN: {initial_parameters[1]}',
                    f'FP: {initial_parameters[2]}',
                    f'FN: {initial_parameters[3]}',
                    f'sencitivity: {sensitivity}',
                    f'precision: {precision}',
                    f'F1 score: {f1_score}',
                    f'accuracy: {accuracy}'
                    ''
                    ]
            print('\n'.join(output_lines))

        if output_type == 'graph':
            x_axis = ['TP', 'TN', 'FP', 'FN']
            colors = ['blue', 'green', 'red', 'yellow']
            plt.bar(x_axis, ACMG_criteria_validation[criteria], color=colors)
            note_string = f'sencitivity: {sensitivity}, precision: {precision}, F1 score: {f1_score}, accuracy: {accuracy}'
            plt.title(test_id + ' - ' + criteria + ': ' + '\n' + note_string)
            plt.xlabel('Parameters')
            plt.ylabel('Matched amount')
            plt.savefig(test_id + '_' + criteria + '.png')


def cli_interface() -> tuple[str, str, str]:
    parser = argparse.ArgumentParser(description='List parameter name and parameter value')
    parser.add_argument('--results', type=str, required=True)
    parser.add_argument('--groundtruth', type=str, default='no')
    parser.add_argument('--output', type=str, default='cli')
    arguments = parser.parse_args()

    return arguments.results, arguments.groundtruth, arguments.output


if __name__ == "__main__":
    test_results_file, gt, output = cli_interface()
    with open('experiment.json', 'r') as file:
        test_results_data = json.load(file)
        parse_test_results(test_results_data['variantsAnalised'])
        make_analysis(gt)
        make_output(output, test_results_data['testId'])

