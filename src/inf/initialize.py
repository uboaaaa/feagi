

import logging
import os
import string
import random
from queue import Queue
from threading import Thread
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from datetime import datetime
from collections import deque
from inf import runtime_data, disk_ops, settings
from configparser import ConfigParser
from shutil import copyfile
from evo.stats import list_top_n_utf_memory_neurons


log = logging.getLogger(__name__)


def run_id_gen(size=6, chars=string.ascii_uppercase + string.digits):
    """
    This function generates a unique id which will be associated with each neuron
    :param size:
    :param chars:
    :return:

    Rand gen source partially from:
    http://stackoverflow.com/questions/2257441/random-string-generation-with-upper-case-letters-and-digits-in-python
    """
    runtime_data.brain_run_id = \
        (str(datetime.now()).replace(' ', '_')).replace('.', '_')+'_'+(''.join(random.choice(chars)
                                                                               for _ in range(size)))+'_R'


def init_parameters(ini_path='./feagi_configuration.ini'):
    """To load all the key configuration parameters"""
    feagi_config = ConfigParser()
    feagi_config.read(ini_path)
    runtime_data.parameters = {s: dict(feagi_config.items(s)) for s in feagi_config.sections()}
    log.info("All parameters have been initialized.")


def init_working_directory():
    """
    Creates needed folder structure as the working directory for FEAGI. This includes a folder to house connectome
    as well as folders needed for IPU/OPU to ingress/egress data accordingly.

    """
    runtime_data.working_directory = runtime_data.parameters["InitData"]["working_directory"] + '/' + runtime_data.brain_run_id

    # Create connectome directory if needed
    # todo: need to consolidate the connectome path as currently captured in two places
    runtime_data.connectome_path = runtime_data.working_directory + '/connectome/'
    runtime_data.parameters["InitData"]["connectome_path"] = runtime_data.connectome_path
    if not os.path.exists(runtime_data.connectome_path):
        os.makedirs(runtime_data.connectome_path)
    # copyfile(runtime_data.parameters["InitData"]["static_genome_path"], runtime_data.connectome_path + '/')

    # Create IPU directories if needed
    # todo: figure best way to obtain the following list. possibly from genome
    directory_list = ['ipu', 'opu_vision', 'opu_utf', 'opu_auditory']
    for _ in directory_list:
        ipu_path = runtime_data.working_directory + '/' + _
        if not os.path.exists(ipu_path):
            os.makedirs(ipu_path)
        runtime_data.paths[_] = runtime_data.working_directory + _
    print(runtime_data.paths)


def init_genome():
    # The following stages the genome in the proper connectome path and loads it into the memory
    disk_ops.genome_handler(runtime_data.connectome_path)


def init_cortical_list():
    cortical_list = []
    for key in runtime_data.genome['blueprint']:
        cortical_list.append(key)
    runtime_data.cortical_list = cortical_list


def init_data_sources():
    """To validate and initialize all data sources and databases"""
    log.info("All data sources have been initialized.")
    return


def initialize():
    run_id_gen()
    init_parameters()
    init_working_directory()
    init_genome()
    init_cortical_list()
    init_data_sources()


def init_burst_engine():
    print("\n\n")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("**** **** **** **** ****       Starting the burst_manager engine...        **** **** ****")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("**** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** **** ****")
    print("\n\n")

    print(runtime_data.parameters['Switches']['use_static_genome'])

    # Initializing the comprehension queue
    disk_ops.genome_handler(runtime_data.parameters['InitData']['connectome_path'])
    # todo: Move comprehension span to genome that is currently in parameters
    comprehension_span = int(runtime_data.parameters["InitData"]["comprehension_span"])
    runtime_data.comprehension_queue = deque(['-'] * comprehension_span)
    runtime_data.parameters["Auto_injector"]["injector_status"] = False
    runtime_data.termination_flag = False
    runtime_data.top_10_utf_memory_neurons = list_top_n_utf_memory_neurons("utf8_memory", 10)
    runtime_data.top_10_utf_neurons = list_top_n_utf_memory_neurons("utf8", 10)
    runtime_data.v1_members = []

    for item in runtime_data.cortical_list:
        if runtime_data.genome['blueprint'][item]['sub_group_id'] == "vision_v1":
            runtime_data.v1_members.append(item)


def exit_burst_process():
    print(settings.Bcolors.YELLOW + '>>>Burst Exit criteria has been met!   <<<' + settings.Bcolors.ENDC)
    runtime_data.live_mode_status = 'idle'
    runtime_data.burst_count = 0
    runtime_data.parameters["Switches"]["ready_to_exit_burst"] = True
    runtime_data.parameters["Auto_injector"]["injector_status"] = False
    if runtime_data.parameters["Switches"]["capture_brain_activities"]:
        disk_ops.save_fcl_to_disk()

