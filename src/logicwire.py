#Import the MonoSAT library
from monosat import *
import converts
import operator
import baseutils
import time
import copy
import operator
from random import randint

LOGIC_VALUE_ZERO = "0"
LOGIC_VALUE_ONE = "1"
LOGIC_VALUE_X = "X"

PRIMARY_INPUT = "pin"
PRIMARY_OUTPUT = "pout"
KEY_INPUT = "kin"
INTERMEDIATE_WIRE = "inwire"

ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0


class wire:
    def __init__(self, name, type, operands, logic_value, logic_level, logic_level_min, catg, index):
        self.name = name
        self.type = type
        self.operands = operands
        self.logic_value = logic_value
        self.logic_level = logic_level
        self.logic_level_min = logic_level_min
        self.catg = catg
        self.index = index

def wire_print(wire_in, print_mode):
    baseutils.h_print(print_mode, "w_name: ", wire_in.name)
    baseutils.h_print(print_mode, "w_type: ", wire_in.type)
    for i in range(0, len(wire_in.operands)):
        baseutils.h_print(print_mode, "w_opr", i, ": ", wire_in.operands[i].name)
    baseutils.h_print(print_mode, "w_valu: ", wire_in.logic_value)
    baseutils.h_print(print_mode, "w_glevmax: ", wire_in.logic_level)
    baseutils.h_print(print_mode, "w_glevmin: ", wire_in.logic_level_min)
    baseutils.h_print(print_mode, "catg: ", wire_in.catg)
    baseutils.h_print(print_mode, "index: ", wire_in.index)
    baseutils.h_print(print_mode, "-------------------")

def wire_dep(benchmark_address):
    wires = []
    pinwires = []
    keywires = []
    temp = []
    interwires = []
    outputs = []
    poutwires = []
    bench_file = open(benchmark_address)

    pinindex = 0
    poutindex = 0
    kinindex = 0
    inwireindex = 0

    found = False

    for line in bench_file:
        if "INPUT" in line:
            if "key" in line:
                current_wire = wire(line[line.find("(") + 1:line.find(")")], "inp", [], LOGIC_VALUE_ONE, 0, 0, KEY_INPUT, kinindex)
                kinindex = kinindex + 1
                keywires.append(current_wire)
            else:
                current_wire = wire(line[line.find("(") + 1:line.find(")")], "inp", [], LOGIC_VALUE_ONE, 0, 0, PRIMARY_INPUT, pinindex)
                pinindex = pinindex + 1
                pinwires.append(current_wire)
            wires.append(current_wire)
        elif "OUTPUT" in line:
            outputs.append(line[line.find("(") + 1:line.find(")")])
        elif " = " in line:
            gate_out = line[0: line.find(" =")]
            gate_type = line[line.find("= ") + 2: line.find("(")]
            gate_list_inputs = line[line.find("(") + 1:line.find(")")]
            gate_oprs = gate_list_inputs.split(", ")
            for i in range(0, len(gate_oprs)):
                found = False
                for j in range(0, len(wires)):
                    if wires[j].name == gate_oprs[i]:
                        found = True
                        temp.append(wires[j])
                        break
                if not found:
                    catg_dummy = INTERMEDIATE_WIRE
                    ind_dummy = inwireindex
                    for j in range(0, len(outputs)):
                        if gate_oprs[i] == outputs[j]:
                            catg_dummy = PRIMARY_OUTPUT
                            ind_dummy = poutindex
                    temp.append(wire(gate_oprs[i], "dummy", [], LOGIC_VALUE_ONE, 0, 1000, catg_dummy, ind_dummy))

            max_level = 0
            min_level = 1000

            for i in range(0, len(temp)):
                if temp[i].logic_level > max_level:
                    max_level = temp[i].logic_level

            for i in range(0, len(temp)):
                if temp[i].logic_level_min < min_level:
                    min_level = temp[i].logic_level_min

            if gate_out in outputs:
                current_wire = wire(gate_out, gate_type, temp, LOGIC_VALUE_ONE, max_level + 1, min_level + 1, PRIMARY_OUTPUT, poutindex)
                wires.append(current_wire)
                poutindex = poutindex + 1
                poutwires.append(current_wire)
            else:
                current_wire = wire(gate_out, gate_type, temp, LOGIC_VALUE_ONE, max_level + 1, min_level + 1, INTERMEDIATE_WIRE, inwireindex)
                wires.append(current_wire)
                inwireindex = inwireindex + 1
                interwires.append(current_wire)
            temp = []
    bench_file.close()

    for i in range(0, len(wires)):
        for j in range(0, len(wires[i].operands)):
            if wires[i].operands[j].type == "dummy":
                found = False
                for k in range(0, len(wires)):
                    if wires[k].name == wires[i].operands[j].name:
                        found = True
                        wires[i].operands[j] = wires[k]
                        break
                if not found:
                    baseutils.h_print(ERR_PR, wires[i].operands[j].name, " --> ERROR1 in read_bench()")
                    exit()

    for i in range(0, len(wires)):
        wires[i].logic_level = -1

    toposort_done = -1
    while toposort_done == -1:
        toposort_done = 0
        for i in range(0, len(wires)):
            if wires[i].catg == PRIMARY_INPUT or wires[i].catg == KEY_INPUT:
                wires[i].logic_level = 0
            else:
                max_level = 0
                min_level = 1000
                cur_lglev = 0
                for j in range(0, len(wires[i].operands)):
                    if wires[i].operands[j].logic_level > max_level:
                        max_level = wires[i].operands[j].logic_level
                    elif wires[i].operands[j].logic_level == -1:
                        toposort_done = -1
                        cur_lglev = -1
                if cur_lglev == 0:
                    wires[i].logic_level = max_level + 1

                for j in range(0, len(wires[i].operands)):
                    if wires[i].operands[j].logic_level_min < min_level:
                        min_level = wires[i].operands[j].logic_level_min
                    elif wires[i].operands[j].logic_level_min == -1:
                        toposort_done = -1
                        cur_lglev = -1
                if cur_lglev == 0:
                    wires[i].logic_level_min = min_level + 1

    # wires.sort(key=operator.attrgetter('logic_level'))

    pinwires = []
    keywires = []
    interwires = []
    poutwires = []

    for i in range(0, len(wires)):
        if wires[i].catg == PRIMARY_INPUT:
            pinwires.append(wires[i])
        elif wires[i].catg == KEY_INPUT:
            keywires.append(wires[i])
        elif wires[i].catg == INTERMEDIATE_WIRE:
            interwires.append(wires[i])
        elif wires[i].catg == PRIMARY_OUTPUT:
            poutwires.append(wires[i])

    interwires.sort(key=operator.attrgetter('logic_level'))

    wires = pinwires + keywires + interwires + poutwires

    pinwires = []
    keywires = []
    interwires = []
    poutwires = []

    pinindex = 0
    poutindex = 0
    kinindex = 0
    inwireindex = 0

    for i in range(0, len(wires)):
        if wires[i].catg == PRIMARY_INPUT:
            wires[i].index = pinindex
            pinindex += 1
            pinwires.append(wires[i])
        elif wires[i].catg == KEY_INPUT:
            wires[i].index = kinindex
            kinindex += 1
            keywires.append(wires[i])
        elif wires[i].catg == INTERMEDIATE_WIRE:
            wires[i].index = inwireindex
            inwireindex += 1
            interwires.append(wires[i])
        elif wires[i].catg == PRIMARY_OUTPUT:
            wires[i].index = poutindex
            poutindex += 1
            poutwires.append(wires[i])

    wires = pinwires + keywires + interwires + poutwires

    return wires, pinwires, keywires, interwires, poutwires



def logic_simulation(input_value, wires): #using SAT solver TODO:test performance

    j = 0
    for i in range(0,len(wires)):
        wires[i].logic_value = LOGIC_VALUE_X
    for i in range(0,len(wires)):
        if wires[i].type == "inp":
            wires[i].logic_value = input_value[j]
            j += 1
        elif wires[i].type == "NOT" or wires[i].type == "not":
            if wires[i].operands[0].logic_value == LOGIC_VALUE_ZERO:
                wires[i].logic_value = LOGIC_VALUE_ONE
            elif wires[i].operands[0].logic_value == LOGIC_VALUE_ONE:
                wires[i].logic_value = LOGIC_VALUE_ZERO
            else:
                baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")

        elif wires[i].type == "BUFF" or wires[i].type == "buff" or wires[i].type == "BUF" or wires[i].type == "buf":
            if wires[i].operands[0].logic_value == LOGIC_VALUE_ZERO:
                wires[i].logic_value = LOGIC_VALUE_ZERO
            elif wires[i].operands[0].logic_value == LOGIC_VALUE_ONE:
                wires[i].logic_value = LOGIC_VALUE_ONE
            else:
                baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")

        elif wires[i].type == "NAND" or wires[i].type == "nand":
            temp_value = LOGIC_VALUE_ZERO
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ZERO:
                    temp_value = LOGIC_VALUE_ONE
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            wires[i].logic_value = temp_value

        elif wires[i].type == "AND" or wires[i].type == "and":
            temp_value = LOGIC_VALUE_ONE
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ZERO:
                    temp_value = LOGIC_VALUE_ZERO
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            wires[i].logic_value = temp_value

        elif wires[i].type == "OR" or wires[i].type == "or":
            temp_value = LOGIC_VALUE_ZERO
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ONE:
                    temp_value = LOGIC_VALUE_ONE
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            wires[i].logic_value = temp_value

        elif wires[i].type == "NOR" or wires[i].type == "nor":
            temp_value = LOGIC_VALUE_ONE
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ONE:
                    temp_value = LOGIC_VALUE_ZERO
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            wires[i].logic_value = temp_value

        elif wires[i].type == "XOR" or wires[i].type == "xor":
            temp_value = LOGIC_VALUE_ZERO
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ONE and temp_value == LOGIC_VALUE_ZERO:
                    temp_value = LOGIC_VALUE_ONE
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_ONE and temp_value == LOGIC_VALUE_ONE:
                    temp_value = LOGIC_VALUE_ZERO
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            wires[i].logic_value = temp_value

        elif wires[i].type == "XNOR" or wires[i].type == "xnor":
            temp_value = LOGIC_VALUE_ZERO
            for k in range(0, len(wires[i].operands)):
                if wires[i].operands[k].logic_value == LOGIC_VALUE_ONE and temp_value == LOGIC_VALUE_ZERO:
                    temp_value = LOGIC_VALUE_ONE
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_ONE and temp_value == LOGIC_VALUE_ONE:
                    temp_value = LOGIC_VALUE_ZERO
                elif wires[i].operands[k].logic_value == LOGIC_VALUE_X:
                    baseutils.h_print(ERR_PR, "the value of ", wires[i].name, "is not defined")
            if temp_value == LOGIC_VALUE_ONE:
                wires[i].logic_value = LOGIC_VALUE_ZERO
            elif temp_value == LOGIC_VALUE_ZERO:
                wires[i].logic_value = LOGIC_VALUE_ONE
        else:
            baseutils.h_print(ERR_PR, "the operation ", wires[i].type, " is not valid")

    out_res = ""

    for i in range(0, len(wires)):
        if wires[i].catg == PRIMARY_OUTPUT:
            out_res += wires[i].logic_value

    return out_res

def var_log_sim(input_value, wires, iter):

    int_out_value = 0
    for i in range(0, len(input_value)):
        if str(input_value[i].value()) == "True":
            int_out_value += pow(2, i)

    bin_format_value = converts.int2bin(int_out_value, len(input_value))
    org_out_res = logic_simulation(bin_format_value[::-1], wires)

    orgcirc = [None] * len(org_out_res)
    for i in range(0, len(org_out_res)):
        orgcirc[i] = Var()
        if org_out_res[i] == "1":
            orgcirc[i] = Var(true())
        else:
            orgcirc[i] = Var(false())
        orgcirc[i].symbol = "orgcirc_" + str(iter) + "_" + str(i)

    return orgcirc