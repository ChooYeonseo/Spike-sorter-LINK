#! /usr/bin/env python3

"""Module to read Intan Technologies RHD2000 data file generated by
acquisition software (IntanRHX, or legacy Recording Controller / USB
Evaluation Board software).
"""

import sys
import os
import time
import json
import numpy as np
import matplotlib.pyplot as plt

from intanutil.header import (read_header,
                              header_to_result)
from intanutil.data import (calculate_data_size,
                            read_all_data_blocks,
                            check_end_of_file,
                            parse_data,
                            data_to_result)
from intanutil.filter import apply_notch_filter


class experiment:
    def __init__(self, name: str, file_dir: str, save_dif:str = None):
        self.name = name
        self.file_dir = file_dir
        self.save_dif = file_dir if save_dif == None else save_dif
        cnt = 0
        temp_list = []
        for root, dirs, files in os.walk(self.file_dir):
            for file in files:
                if file.endswith('.rhd'):
                    temp_list.append(os.path.join(root, file))
                    cnt += 1
        print("Total {} rhd file has been located.".format(cnt - 1))
        temp_list.pop()
        # print(temp_list)
        self.dir_list = temp_list
        self.experiment_attribute = []

        for filename in self.dir_list:
            self.experiment_attribute.append(self.read_data(filename))
    
        
    def read_data(self, filename):
        """Reads Intan Technologies RHD2000 data file generated by acquisition
        software (IntanRHX, or legacy Recording Controller / USB Evaluation
        board software).

        Data are returned in a dictionary, for future extensibility.
        """
        # Start measuring how long this read takes.

        tic = time.time()

        # Open file for reading.
        with open(filename, 'rb') as fid:

            # Read header and summarize its contents to console.
            header = read_header(fid)

            # Calculate how much data is present and summarize to console.
            data_present, filesize, num_blocks, num_samples = (
                calculate_data_size(header, filename, fid))

            # If .rhd file contains data, read all present data blocks into 'data'
            # dict, and verify the amount of data read.
            if data_present:
                data = read_all_data_blocks(header, num_samples, num_blocks, fid)
                check_end_of_file(filesize, fid)

        # Save information in 'header' to 'result' dict.
        result = {}
        header_to_result(header, result)

        # If .rhd file contains data, parse data into readable forms and, if
        # necessary, apply the same notch filter that was active during recording.
        if data_present:
            parse_data(header, data)
            apply_notch_filter(header, data)

            # Save recorded data in 'data' to 'result' dict.
            data_to_result(header, data, result)

        # Otherwise (.rhd file is just a header for One File Per Signal Type or
        # One File Per Channel data formats, in which actual data is saved in
        # separate .dat files), just return data as an empty list.
        else:
            data = []

        # Report how long read took.
        print('Done!  Elapsed time: {0:0.1f} seconds'.format(time.time() - tic))

        return result
    
    def show_data(self, data_number:int,title:str = None, y_min:float = -300.0, y_max:float = 300.0):
        focused_data = self.experiment_attribute[data_number]
        channel_number = len(focused_data["amplifier_data"])

        fig, ax = plt.subplots(channel_number, 1)
        if title == None:
            fig.suptitle("Loaded Intan Data")
        else:
            fig.suptitle(title)

        ax[-1].set_xlabel("time")
        for i, channel_data in enumerate(focused_data["amplifier_data"]):
            ax[i].set_ylabel(focused_data["amplifier_channels"][i]["native_channel_name"],color='red')
            ax[i].plot(focused_data['t_amplifier'], channel_data, color='black')
            ax[i].margins(x=0, y=0)
            ax[i].set_ylim(y_min, y_max)
        plt.show()

            
        

    def getdata_list(self):
        return self.experiment_attribute
    

# if __name__ == '__main__':
#     a = read_data(sys.argv[1])
#     print(a)

#     fig, ax = plt.subplots(7, 1)

#     for i in range(7):
#         ax[i].set_ylabel('Amp')
#         ax[i].plot(a['t_amplifier'], a['amplifier_data'][i, :])
#         ax[i].margins(x=0, y=0)



    # ax[1].set_ylabel('Aux')
    # ax[1].plot(a['t_aux_input'], a['aux_input_data'][0, :])
    # ax[1].margins(x=0, y=0)

    # ax[2].set_ylabel('Vdd')
    # ax[2].plot(a['t_supply_voltage'], a['supply_voltage_data'][0, :])
    # ax[2].margins(x=0, y=0)

    # ax[3].set_ylabel('ADC')
    # ax[3].plot(a['t_board_adc'], a['board_adc_data'][0, :])
    # ax[3].margins(x=0, y=0)

    # ax[4].set_ylabel('Digin')
    # ax[4].plot(a['t_dig'], a['board_dig_in_data'][0, :])
    # ax[4].margins(x=0, y=0)

    # ax[5].set_ylabel('Digout')
    # ax[5].plot(a['t_dig'], a['board_dig_out_data'][0, :])
    # ax[5].margins(x=0, y=0)

    # ax[6].set_ylabel('Temp')
    # ax[6].plot(a['t_temp_sensor'], a['temp_sensor_data'][0, :])
    # ax[6].margins(x=0, y=0)

    # plt.show()
