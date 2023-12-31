# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 19:08:25 2021

@author: Manuel Camargo
"""
import os
import subprocess

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import sys
import getopt
import shutil

from model_prediction import model_predictor as pr
import support_functions as sf
from support_modules import stochastic_model as sm
from support_modules import models_merger as mm

# =============================================================================
# Main function
# =============================================================================
def catch_parameter(opt):
    """Change the captured parameters names"""
    switch = {'-h': 'help', '-a': 'activity', '-c': 'folder',
              '-b': 'model_file', '-v': 'variant', '-r': 'rep'}
    return switch.get(opt)

def call_simod(file_name):
    print('----------------------------------------------------------------------')
    print('-------------------     RUNNING SIMOD    -----------------------------')
    print('----------------------------------------------------------------------')

    simod_files = os.listdir(os.path.join('input_files', 'simod'))

    #Copy event log file to Simod
    try:
        source_file = os.path.join('input_files', file_name)
        destination_file = os.path.join('..', 'Simod-2.3.1','inputs', file_name)
        print(source_file)
        print(destination_file)
        shutil.copy(source_file, destination_file)
        
    except FileNotFoundError as e:
        print(e)
        exit(1)

    if file_name not in simod_files:

        os.chdir('../Simod-2.3.1/')
        bash_command = 'bash.sh'
        subprocess.run([bash_command, file_name], shell=True)
        os.chdir('../GenerativeLSTM/')
    
    #Delete event log file from Simod
    os.remove(destination_file)

def call_spmd(parameters):
    print('----------------------------------------------------------------------')
    print('--------------  RUNNING Stochastic Process Model  --------------------')
    print('----------------------------------------------------------------------')
    print("time format " + parameters['read_options']['timeformat'])
    print("column_names")
    print(parameters['read_options']['column_names'])
    print("one_timestamp")
    print(parameters['read_options']['one_timestamp'])
    print("filter_d_attrib")
    print(parameters['read_options']['filter_d_attrib'])
    print("file")
    print(parameters['filename'].split('.')[0])
    print("sm3_path")
    print(parameters['sm3_path'])
    print("bimp_path")
    print(parameters['bimp_path'])
    print("concurrency")
    print(parameters['concurrency'])
    print("epsilon")
    print(parameters['epsilon'])
    print("eta")
    print(parameters['eta'])
    settings = dict()
    settings['timeformat'] = parameters['read_options']['timeformat']
    settings['column_names'] = parameters['read_options']['column_names']
    settings['one_timestamp'] = parameters['read_options']['one_timestamp']
    settings['filter_d_attrib'] = parameters['read_options']['filter_d_attrib']

    settings['file'] = parameters['filename'].split('.')[0]
    settings['sm3_path'] = parameters['sm3_path']

    settings['bimp_path'] = parameters['bimp_path']
    settings['concurrency'] = parameters['concurrency']
    settings['epsilon'] = parameters['epsilon']
    settings['eta'] = parameters['eta']

    settings['log_path'] = os.path.join('input_files', settings['file'] + '.xes')
    settings['tobe_bpmn_path'] = os.path.join('input_files', 'spmd', settings['file'] + '.bpmn')
    print("log_path")
    print(os.path.join('input_files', settings['file'] + '.xes'))
    print("tobe_bpmn_path")
    print(os.path.join('input_files', 'spmd', settings['file'] + '.bpmn'))
    spmd = sm.StochasticModel(settings)
    return spmd

def call_merger(parameters, spmd):
    print('----------------------------------------------------------------------')
    print('---------------------------  RUNNING MERGER --------------------------')
    print('----------------------------------------------------------------------')
    settings = dict()
    settings['file'] = parameters['filename'].split('.')[0]
    settings['bimp_path'] = parameters['bimp_path']
    settings['tobe_bpmn_path'] = os.path.join('input_files', 'spmd', settings['file'] + '.bpmn')
    settings['asis_bpmn_path'] = os.path.join('input_files', 'simod', settings['file'] + '.bpmn')
    settings['csv_output_path'] = os.path.join('output_files', 'simulation_stats', settings['file'] + '.csv')
    settings['output_path'] = os.path.join('output_files', 'simulation_files', settings['file'] + '.bpmn')
    settings['lrs'] = spmd.lrs
 

    mod_mer = mm.MergeModels(settings)

def main(argv):
    parameters = dict()
    column_names = {'Case ID': 'caseid',
                    'Activity': 'task',
                    'lifecycle:transition': 'event_type',
                    'Resource': 'user'}
    parameters['one_timestamp'] = False  # Only one timestamp in the log
    parameters['include_org_log'] = False
    parameters['read_options'] = {

        #Production and Purchasing: "%Y-%m-%d %H:%M:%S%z"
        #RunningExample: "%Y-%m-%d %H:%M:%S%z"
        #ConsultaDataMining201618: "%Y-%m-%d %H:%M:%S%z"

        'timeformat': "%Y-%m-%d %H:%M:%S%Z",
        'column_names': column_names,
        'one_timestamp': parameters['one_timestamp'],
        'filter_d_attrib': False}
    
    parameters['filename'] = 'ConsultaDataMining201618.xes'
    parameters['input_path'] = 'input_files'

    parameters['sm3_path'] = os.path.join('external_tools', 'splitminer3', 'bpmtk.jar')
    parameters['bimp_path'] = os.path.join('external_tools', 'bimp', 'qbp-simulator-engine_with_csv_statistics.jar')
    parameters['concurrency'] = 0.0
    parameters['epsilon'] = 0.5
    parameters['eta'] = 0.7
    
    # Parameters settled manually or catched by console for batch operations
    if not argv:
        # predict_next, pred_sfx
        parameters['activity'] = 'pred_log'

        #PurchasingExample:'20230901_D4F6CAA8_47EF_45DD_B2E7_7EB998EBAE91' 
        #Production: '20230615_FF2C5479_8FD9_4E8A_9473_F298F8D2618D'
        #RunningExample: '20230901_B93F97FD_D150_422E_8E5F_550A398E3AD4'
        #ConsultaDataMining201618: '20230901_3132D4F9_9047_429D_BAD8_C983228B2526'
        
        parameters['folder'] = '20230901_3132D4F9_9047_429D_BAD8_C983228B2526'
        parameters['model_file'] = parameters['filename'].split('.')[0] + '.h5'
        parameters['log_name'] = parameters['model_file'].split('.')[0]
        parameters['is_single_exec'] = False  # single or batch execution
        # variants and repetitions to be tested Random Choice, Arg Max, Rules Based Random Choice, Rules Based Arg Max
        parameters['variant'] = 'Rules Based Random Choice'
        parameters['rep'] = 1
    else:
        # Catch parms by console
        try:
            opts, _ = getopt.getopt(argv, "ho:a:f:c:b:v:r:",
                                    ['one_timestamp=', 'activity=', 'folder=',
                                     'model_file=', 'variant=', 'rep='])
            for opt, arg in opts:
                key = catch_parameter(opt)
                if key in ['rep']:
                    parameters[key] = int(arg)
                else:
                    parameters[key] = arg
        except getopt.GetoptError:
            print('Invalid option')
            sys.exit(2)
    print(parameters['folder'])
    print(parameters['model_file'])

    # Call Simod
    call_simod(parameters['filename'])

    #Generative model prediction
    pr.ModelPredictor(parameters)

    #Call SPMD
    spmd = call_spmd(parameters)

    #Call Merger
    call_merger(parameters, spmd)

if __name__ == "__main__":
    main(sys.argv[1:])
