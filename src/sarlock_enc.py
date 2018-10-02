#Import the MonoSAT library
import os
import baseutils
import copy
import time
import copy
import operator
from random import *

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

if __name__ == "__main__":

    baseutils.h_print(WAR_PR, "************************ Starting dll_replace **********************")

    rnd_obf_bench_address = sys.argv[1]     # sys.argv[1] > original bench name
    sar_rnd_obf_bench_address = sys.argv[2]
    key_str = sys.argv[3]

    bench_file = open(rnd_obf_bench_address)
    rnd_key_cnt = 0

    inp_list = []

    xor_gates = ""
    flip_sig = ""
    mask_sig = ""
    not_key_list = ""
    new_keys_str = ""

    old_keys_str = ""
    output_str = ""
    input_str = ""
    gates_str = ""

    selected_output = ""


    for line in bench_file:
        if "INPUT(keyinput" in line:
            rnd_key_cnt += 1
            old_keys_str += line
        elif "INPUT" in line:
            inp_list.append(line[line.find("(") + 1:line.find(")")])
            input_str += line
        elif "OUTPUT" in line:
            selected_output = line[line.find("(") + 1:line.find(")")]
            output_str += line
        elif " = " in line:
            gates_str += line

    bench_file.close()

    for i in range(0, len(inp_list)):
        xor_gates += "nXoR" + str(i) + " = XOR(" + inp_list[i] + ", " + "keyinput" + str(i+rnd_key_cnt) + ")\n"
        new_keys_str += "INPUT(keyinput" + str(i+rnd_key_cnt) + ")\n"

    flip_sig_list = ""
    if len(inp_list) < 10:
        for i in range(0, len(inp_list)):
            if i == 0:
                flip_sig = "flipSig = NOR(nXoR" + str(i) + ", "
            elif i == len(inp_list) - 1:
                flip_sig += "nXoR" + str(i) + ")\n"
            else:
                flip_sig += "nXoR" + str(i) + ", "
    else:
        cnt_flip_list = int(len(inp_list)/10) + 1
        for i in range(0, int(len(inp_list)/10)):
            for j in range(0, 10):
                if j == 0:
                    flip_sig = "flipSig" + str(i) + " = OR(nXoR" + str(i*10 + j) + ", "
                elif j == 9:
                    flip_sig += "nXoR" + str(i*10 + j) + ")\n"
                else:
                    flip_sig += "nXoR" + str(i*10 + j) + ", "
            flip_sig_list += flip_sig
        for i in range(int(len(inp_list)/10)*10 + 1, len(inp_list)):
            if i == int(len(inp_list) / 10) * 10 + 1:
                flip_sig = "flipSig" + str(int(len(inp_list)/10)) + " = OR(nXoR" + str(i) + ", "
            elif i == len(inp_list) - 1:
                flip_sig += "nXoR" + str(i) + ")\n"
            else:
                flip_sig += "nXoR" + str(i) + ", "
        flip_sig_list += flip_sig

        for i in range(0, cnt_flip_list):
            if i == 0:
                flip_sig = "flipSig = NOR(flipSig" + str(i) + ", "
            elif i == cnt_flip_list - 1:
                flip_sig += "flipSig" + str(i) + ")\n"
            else:
                flip_sig += "flipSig" + str(i) + ", "

    for i in range(0, len(key_str)):
        not_key_list += "not_keyinp" + str(i+rnd_key_cnt) + " = NOT(keyinput" + str(i+rnd_key_cnt) + ")\n"

    mask_sig_list = ""
    if len(inp_list) < 10:
        for i in range(0, len(inp_list)):
            if i == 0:
                if key_str[i] == "0":
                    mask_sig = "maskSig = AND(not_keyinp" + str(i+rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig = "maskSig = AND(keyinput" + str(i + rnd_key_cnt) + ", "
            elif i == len(inp_list) - 1:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i+rnd_key_cnt) + ")\n"
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i+rnd_key_cnt) + ")\n"
            else:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i+rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i+rnd_key_cnt) + ", "
    else:
        cnt_mask_list = int(len(inp_list) / 10) + 1
        for i in range(0, int(len(inp_list) / 10)):
            for j in range(0, 10):
                if j == 0:
                    if key_str[j] == "0":
                        mask_sig = "maskSig" + str(i) + " = AND(not_keyinp" + str(i*10 + j + rnd_key_cnt) + ", "
                    elif key_str[i] == "1":
                        mask_sig = "maskSig" + str(i) + " = AND(keyinput" + str(i * 10 + j + rnd_key_cnt) + ", "
                elif j == 9:
                    if key_str[j] == "0":
                        mask_sig += "not_keyinp" + str(i*10 + j + rnd_key_cnt) + ")\n"
                    elif key_str[i] == "1":
                        mask_sig += "keyinput" + str(i*10 + j + rnd_key_cnt) + ")\n"
                else:
                    if key_str[i] == "0":
                        mask_sig += "not_keyinp" + str(i*10 + j + rnd_key_cnt) + ", "
                    elif key_str[i] == "1":
                        mask_sig += "keyinput" + str(i*10 + j + rnd_key_cnt) + ", "
            mask_sig_list += mask_sig

        for i in range(int(len(inp_list) / 10) * 10, len(inp_list)):
            if i == int(len(inp_list) / 10) * 10:
                if key_str[i] == "0":
                    mask_sig = "maskSig" + str(int(len(inp_list)/10)) + " = AND(not_keyinp" + str(i + rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig = "maskSig" + str(int(len(inp_list)/10)) + " = AND(keyinput" + str(i + rnd_key_cnt) + ", "
            elif i == len(inp_list) - 1:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i + rnd_key_cnt) + ")\n"
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i + rnd_key_cnt) + ")\n"
            else:
                if key_str[i] == "0":
                    mask_sig += "not_keyinp" + str(i + rnd_key_cnt) + ", "
                elif key_str[i] == "1":
                    mask_sig += "keyinput" + str(i + rnd_key_cnt) + ", "
        mask_sig_list += mask_sig

        for i in range(0, cnt_mask_list):
            if i == 0:
                mask_sig = "maskSig = AND(maskSig" + str(i) + ", "
            elif i == cnt_mask_list - 1:
                mask_sig += "maskSig" + str(i) + ")\n"
            else:
                mask_sig += "maskSig" + str(i) + ", "

    not_mask = "not_mask = NOT(maskSig)\n"
    mask_flip = "flip_mask = AND(flipSig, not_mask)\n"

    new_bench = input_str + "\n" + old_keys_str + "\n" + new_keys_str + "\n" + output_str + "\n" + gates_str + "\n" + xor_gates + "\n" + not_key_list + "\n" + flip_sig_list + "\n" + flip_sig + "\n" + mask_sig_list + "\n" + mask_sig + "\n" + not_mask + "\n" + mask_flip + "\n"
    new_bench = new_bench.replace(selected_output + " = ", selected_output + "_enc = ")

    new_bench += selected_output + " = XOR(" + selected_output + "_enc, flip_mask)\n"


    bench_file = open(sar_rnd_obf_bench_address, "w")
    bench_file.write(new_bench)
    bench_file.close()











