#Import the MonoSAT library
from monosat import *
import os
import logicwire
import converts
import baseutils
import copy
import time
import copy
import operator
from random import randint
import math
from collections import deque

import sys


ERR_PR = 3
WAR_PR = 2
INF_PR = 1
DBG_PR = 0

def dll_tck():

    obf_bench_name = sys.argv[2] + "_dll_" + sys.argv[3] + ".bench"
    obf_bench_address = "../benchmarks/dll_obfuscated/" + obf_bench_name
    extracted_bench_address = "../benchmarks/logic_extracted/" + obf_bench_name
    orig_bench_address = "../benchmarks/originals/" + sys.argv[2] + ".bench"

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)

    exe_non_func_time = time.time()
    delay_keys = baseutils.graph_dep(obf_bench_address, orgpoutwires)
    exe_non_func_time = time.time() - exe_non_func_time
    # g1.draw()

    converts.extract_logic(obf_bench_address)

    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(extracted_bench_address)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    baseutils.h_print(DBG_PR, "-------------obfwires------------")
    for i in range(0, len(obfwires)):
        logicwire.wire_print(obfwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------obfpinwires------------")
    for i in range(0, len(obfpinwires)):
        logicwire.wire_print(obfpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfkeywires--------------")
    for i in range(0, len(obfkeywires)):
        logicwire.wire_print(obfkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfinterwires--------------")
    for i in range(0, len(obfinterwires)):
        logicwire.wire_print(obfinterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfpoutwires--------------")
    for i in range(0, len(obfpoutwires)):
        logicwire.wire_print(obfpoutwires[i], DBG_PR)

    baseutils.h_print(INF_PR, "#############################################################")

    baseutils.h_print(DBG_PR, "-------------orgwires------------")
    for i in range(0, len(orgwires)):
        logicwire.wire_print(orgwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------orgpinwires------------")
    for i in range(0, len(orgpinwires)):
        logicwire.wire_print(orgpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgkeywires--------------")
    for i in range(0, len(orgkeywires)):
        logicwire.wire_print(orgkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orginterwires--------------")
    for i in range(0, len(orginterwires)):
        logicwire.wire_print(orginterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgpoutwires--------------")
    for i in range(0, len(orgpoutwires)):
        logicwire.wire_print(orgpoutwires[i], DBG_PR)

    baseutils.h_print(WAR_PR, "########## looking for DIPs (Iterative SAT Calls)  ##########")

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while res == 1:
        res, dscinp, new_func_time = baseutils.finddip(obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2,
                                                       exe_func_time)  # duplicate and find dip
        orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
        if res == 1:
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")
    func_keys = baseutils.findkey(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc)

    found_keys = delay_keys + func_keys

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "================= Non-functional keys ... ===================")
    baseutils.h_print(INF_PR, "=============================================================")

    if delay_keys:
        for i in range(0, len(delay_keys)):
            baseutils.h_print(INF_PR, delay_keys[i].getSymbol(), " = ", str(delay_keys[i].value()))
    else:
        baseutils.h_print(WAR_PR, "No Non-functional key .............")

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "=================== Functional keys ... =====================")
    baseutils.h_print(INF_PR, "=============================================================")

    for i in range(0, len(func_keys)):
        baseutils.h_print(INF_PR, func_keys[i].getSymbol(), " = ", str(func_keys[i].value()))

    if int(sys.argv[3]) == 0:
        len_key = len(found_keys)
    else:
        len_key = int(sys.argv[3]) * 2
    combined_key = [None] * len_key
    for i in range(0, len(found_keys)):
        key_name = found_keys[i].getSymbol()
        key_index = int(key_name[key_name.find("keyinput") + 8: key_name.find("c")])
        combined_key[key_index] = str(found_keys[i].value())
    # found_keys.sort(key=operator.attrgetter('symbol'))

    correct_key = [None] * len(combined_key)
    for i in range(0, len(combined_key)):
        if combined_key[i] == "True":
            correct_key[i] = "1"
        else:
            correct_key[i] = "0"

    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(ERR_PR, "================ Finish 2D (Eager) solver ... ===============")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")

    baseutils.h_print(ERR_PR, "key= ", ''.join(correct_key))
    baseutils.h_print(ERR_PR, "func_iteration= ", iter, "; func_exe_time= ", exe_func_time, "; nonfunc_exe_time= ",
                      exe_non_func_time)


def sat_tck():

    obf_bench_name = sys.argv[2]
    orig_bench_address = sys.argv[3]

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)
    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(obf_bench_name)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    baseutils.h_print(DBG_PR, "-------------obfwires------------")
    for i in range(0, len(obfwires)):
        logicwire.wire_print(obfwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------obfpinwires------------")
    for i in range(0, len(obfpinwires)):
        logicwire.wire_print(obfpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfkeywires--------------")
    for i in range(0, len(obfkeywires)):
        logicwire.wire_print(obfkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfinterwires--------------")
    for i in range(0, len(obfinterwires)):
        logicwire.wire_print(obfinterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfpoutwires--------------")
    for i in range(0, len(obfpoutwires)):
        logicwire.wire_print(obfpoutwires[i], DBG_PR)

    baseutils.h_print(INF_PR, "#############################################################")

    baseutils.h_print(DBG_PR, "-------------orgwires------------")
    for i in range(0, len(orgwires)):
        logicwire.wire_print(orgwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------orgpinwires------------")
    for i in range(0, len(orgpinwires)):
        logicwire.wire_print(orgpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgkeywires--------------")
    for i in range(0, len(orgkeywires)):
        logicwire.wire_print(orgkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orginterwires--------------")
    for i in range(0, len(orginterwires)):
        logicwire.wire_print(orginterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgpoutwires--------------")
    for i in range(0, len(orgpoutwires)):
        logicwire.wire_print(orgpoutwires[i], DBG_PR)

    baseutils.h_print(WAR_PR, "########## looking for DIPs (Iterative SAT Calls)  ##########")

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while res == 1:
        res, dscinp, new_func_time = baseutils.finddip(obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2,
                                                       exe_func_time)  # duplicate and find dip

        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")
    func_keys = baseutils.findkey(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc)

    found_keys = func_keys

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "========================= keys ... ==========================")
    baseutils.h_print(INF_PR, "=============================================================")

    for i in range(0, len(func_keys)):
        baseutils.h_print(INF_PR, func_keys[i].getSymbol(), " = ", str(func_keys[i].value()))

    combined_key = [None] * len(found_keys)
    for i in range(0, len(found_keys)):
        key_name = found_keys[i].getSymbol()
        key_index = int(key_name[key_name.find("keyinput") + 8: key_name.find("c")])
        combined_key[key_index] = str(found_keys[i].value())
    # found_keys.sort(key=operator.attrgetter('symbol'))

    correct_key = [None] * len(combined_key)
    for i in range(0, len(combined_key)):
        if combined_key[i] == "True":
            correct_key[i] = "1"
        else:
            correct_key[i] = "0"

    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(ERR_PR, "=================== Finish SAT solver ... ===================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")

    baseutils.h_print(ERR_PR, "key= ", ''.join(correct_key))
    baseutils.h_print(ERR_PR, "func_iteration= ", iter, "; func_exe_time= ", exe_func_time, "; nonfunc_exe_time= ",
                      exe_non_func_time)


def ddip_tck():

    obf_bench_name = sys.argv[2]
    orig_bench_address = sys.argv[3]

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)
    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(obf_bench_name)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    baseutils.h_print(DBG_PR, "-------------obfwires------------")
    for i in range(0, len(obfwires)):
        logicwire.wire_print(obfwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------obfpinwires------------")
    for i in range(0, len(obfpinwires)):
        logicwire.wire_print(obfpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfkeywires--------------")
    for i in range(0, len(obfkeywires)):
        logicwire.wire_print(obfkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfinterwires--------------")
    for i in range(0, len(obfinterwires)):
        logicwire.wire_print(obfinterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfpoutwires--------------")
    for i in range(0, len(obfpoutwires)):
        logicwire.wire_print(obfpoutwires[i], DBG_PR)

    baseutils.h_print(INF_PR, "#############################################################")

    baseutils.h_print(DBG_PR, "-------------orgwires------------")
    for i in range(0, len(orgwires)):
        logicwire.wire_print(orgwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------orgpinwires------------")
    for i in range(0, len(orgpinwires)):
        logicwire.wire_print(orgpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgkeywires--------------")
    for i in range(0, len(orgkeywires)):
        logicwire.wire_print(orgkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orginterwires--------------")
    for i in range(0, len(orginterwires)):
        logicwire.wire_print(orginterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgpoutwires--------------")
    for i in range(0, len(orgpoutwires)):
        logicwire.wire_print(orgpoutwires[i], DBG_PR)

    baseutils.h_print(WAR_PR, "########## looking for Double DIPs (Iterative SAT Calls)  ##########")

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyin3 = [None] * len(obfkeywires)
    keyin4 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())

        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())

        keyin3[i] = Var()
        keyin3[i].symbol = obfkeywires[i].name + "_3" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin3[i].getSymbol())

        keyin4[i] = Var()
        keyin4[i].symbol = obfkeywires[i].name + "_4" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin4[i].getSymbol())

        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while res == 1:
        res, dscinp, new_func_time = baseutils.double_dip(obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2, keyin3, keyin4,
                                                       exe_func_time)  # duplicate and find dip

        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")
    func_keys = baseutils.findkey(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc)

    found_keys = func_keys

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "========================= keys ... ==========================")
    baseutils.h_print(INF_PR, "=============================================================")

    for i in range(0, len(func_keys)):
        baseutils.h_print(INF_PR, func_keys[i].getSymbol(), " = ", str(func_keys[i].value()))

    combined_key = [None] * len(found_keys)
    for i in range(0, len(found_keys)):
        key_name = found_keys[i].getSymbol()
        key_index = int(key_name[key_name.find("keyinput") + 8: key_name.find("c")])
        combined_key[key_index] = str(found_keys[i].value())
    # found_keys.sort(key=operator.attrgetter('symbol'))

    correct_key = [None] * len(combined_key)
    for i in range(0, len(combined_key)):
        if combined_key[i] == "True":
            correct_key[i] = "1"
        else:
            correct_key[i] = "0"

    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(ERR_PR, "=================== Finish DDIP solver ... ==================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")

    baseutils.h_print(ERR_PR, "key= ", ''.join(correct_key))
    baseutils.h_print(ERR_PR, "func_iteration= ", iter, "; func_exe_time= ", exe_func_time, "; nonfunc_exe_time= ",
                      exe_non_func_time)


def lazy_smt():

    obf_bench_name = sys.argv[2] + "_dll_" + sys.argv[3] + ".bench"
    obf_bench_address = "../benchmarks/dll_obfuscated/" + obf_bench_name
    dll_muxed = "../benchmarks/dll_muxed/" + obf_bench_name
    orig_bench_address = "../benchmarks/originals/" + sys.argv[2] + ".bench"

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)

    converts.delaybench2muxbench(obf_bench_address)

    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(dll_muxed)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    baseutils.h_print(DBG_PR, "-------------obfwires------------")
    for i in range(0, len(obfwires)):
        logicwire.wire_print(obfwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------obfpinwires------------")
    for i in range(0, len(obfpinwires)):
        logicwire.wire_print(obfpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfkeywires--------------")
    for i in range(0, len(obfkeywires)):
        logicwire.wire_print(obfkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfinterwires--------------")
    for i in range(0, len(obfinterwires)):
        logicwire.wire_print(obfinterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfpoutwires--------------")
    for i in range(0, len(obfpoutwires)):
        logicwire.wire_print(obfpoutwires[i], DBG_PR)

    baseutils.h_print(INF_PR, "#############################################################")

    baseutils.h_print(DBG_PR, "-------------orgwires------------")
    for i in range(0, len(orgwires)):
        logicwire.wire_print(orgwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------orgpinwires------------")
    for i in range(0, len(orgpinwires)):
        logicwire.wire_print(orgpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgkeywires--------------")
    for i in range(0, len(orgkeywires)):
        logicwire.wire_print(orgkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orginterwires--------------")
    for i in range(0, len(orginterwires)):
        logicwire.wire_print(orginterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgpoutwires--------------")
    for i in range(0, len(orgpoutwires)):
        logicwire.wire_print(orgpoutwires[i], DBG_PR)

    baseutils.h_print(WAR_PR, "########## looking for DIPs (Iterative SAT Calls)  ##########")

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    gc_list1 = []
    gc_list2 = []

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    # res, dscinp, new_func_time = baseutils.finddiplazy(obf_bench_address, obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
    #                                                list_orgcirc, keyin1, keyin2, exe_func_time)  # duplicate and find dip
    #
    while res == 1:
        res, dscinp, new_func_time, gc_list1, gc_list2 = baseutils.finddiplazy(obf_bench_address, obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2,
                                                       exe_func_time, gc_list1, gc_list2)  # duplicate and find dip

        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()
    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")
    func_keys = baseutils.findkey(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc)

    found_keys = func_keys

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "========================= keys ... ==========================")
    baseutils.h_print(INF_PR, "=============================================================")

    for i in range(0, len(func_keys)):
        baseutils.h_print(INF_PR, func_keys[i].getSymbol(), " = ", str(func_keys[i].value()))

    combined_key = [None] * len(found_keys)
    for i in range(0, len(found_keys)):
        key_name = found_keys[i].getSymbol()
        key_index = int(key_name[key_name.find("keyinput") + 8: key_name.find("c")])
        combined_key[key_index] = str(found_keys[i].value())
    # found_keys.sort(key=operator.attrgetter('symbol'))

    correct_key = [None] * len(combined_key)
    for i in range(0, len(combined_key)):
        if combined_key[i] == "True":
            correct_key[i] = "1"
        else:
            correct_key[i] = "0"

    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(ERR_PR, "================= Finish 2D (Lazy) solver ... ===============")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")

    baseutils.h_print(ERR_PR, "key= ", ''.join(correct_key))
    baseutils.h_print(ERR_PR, "func_iteration= ", iter, "; func_exe_time= ", exe_func_time, "; nonfunc_exe_time= ",
                      exe_non_func_time)


def appsat_minham_tck():

    obf_bench_name = sys.argv[2]
    orig_bench_address = sys.argv[3]

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)
    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(obf_bench_name)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    timeout_array = deque([20] * 10)
    const_solve = []

    baseutils.h_print(DBG_PR, "-------------obfwires------------")
    for i in range(0, len(obfwires)):
        logicwire.wire_print(obfwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------obfpinwires------------")
    for i in range(0, len(obfpinwires)):
        logicwire.wire_print(obfpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfkeywires--------------")
    for i in range(0, len(obfkeywires)):
        logicwire.wire_print(obfkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfinterwires--------------")
    for i in range(0, len(obfinterwires)):
        logicwire.wire_print(obfinterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------obfpoutwires--------------")
    for i in range(0, len(obfpoutwires)):
        logicwire.wire_print(obfpoutwires[i], DBG_PR)

    baseutils.h_print(INF_PR, "#############################################################")

    baseutils.h_print(DBG_PR, "-------------orgwires------------")
    for i in range(0, len(orgwires)):
        logicwire.wire_print(orgwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-------------orgpinwires------------")
    for i in range(0, len(orgpinwires)):
        logicwire.wire_print(orgpinwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgkeywires--------------")
    for i in range(0, len(orgkeywires)):
        logicwire.wire_print(orgkeywires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orginterwires--------------")
    for i in range(0, len(orginterwires)):
        logicwire.wire_print(orginterwires[i], DBG_PR)

    baseutils.h_print(DBG_PR, "-----------orgpoutwires--------------")
    for i in range(0, len(orgpoutwires)):
        logicwire.wire_print(orgpoutwires[i], DBG_PR)

    baseutils.h_print(WAR_PR, "########## looking for DIPs (Iterative SAT Calls)  ##########")

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    interval = len(orgpoutwires)
    appsat = 0
    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while res != -1 and interval != 0:
        res, dscinp, new_func_time, interval, timeout_array, const_solve = baseutils.finddipham(obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2,
                                                       exe_func_time, interval, timeout_array, const_solve)  # duplicate and find dip

        if len(const_solve) > 50:
            interval = 0
            res = -1
            appsat = 1

        print("res > ", res)
        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        elif res == -2:
            interval -= 1
            if interval == 0:
                res = -1
        elif res == -1 and interval != 0:
            interval -= 1
            res = 1
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")
    func_keys = baseutils.findkey(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc)

    found_keys = func_keys

    baseutils.h_print(INF_PR, "=============================================================")
    baseutils.h_print(INF_PR, "========================= keys ... ==========================")
    baseutils.h_print(INF_PR, "=============================================================")

    for i in range(0, len(func_keys)):
        baseutils.h_print(INF_PR, func_keys[i].getSymbol(), " = ", str(func_keys[i].value()))

    combined_key = [None] * len(found_keys)
    for i in range(0, len(found_keys)):
        key_name = found_keys[i].getSymbol()
        key_index = int(key_name[key_name.find("keyinput") + 8: key_name.find("c")])
        combined_key[key_index] = str(found_keys[i].value())
    # found_keys.sort(key=operator.attrgetter('symbol'))

    correct_key = [None] * len(combined_key)
    for i in range(0, len(combined_key)):
        if combined_key[i] == "True":
            correct_key[i] = "1"
        else:
            correct_key[i] = "0"

    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")
    if appsat == 1:
        baseutils.h_print(ERR_PR, "============= Finish Approximate SAT solver ... =============")
    else:
        baseutils.h_print(ERR_PR, "================= Finish Max Hamm solver ... ================")
    baseutils.h_print(WAR_PR, "=============================================================")
    baseutils.h_print(WAR_PR, "=============================================================")

    baseutils.h_print(ERR_PR, "key= ", ''.join(correct_key))
    baseutils.h_print(ERR_PR, "func_iteration= ", iter, "; func_exe_time= ", exe_func_time, "; nonfunc_exe_time= ",
                      exe_non_func_time)

def sat_cks(dip_no):

    obf_bench_name = sys.argv[3]
    orig_bench_address = sys.argv[4]

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)
    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(obf_bench_name)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while iter < dip_no:
        res, dscinp, new_func_time = baseutils.finddip(obfpinwires, obfkeywires, obfinterwires, obfpoutwires, list_dip,
                                                       list_orgcirc, keyin1, keyin2,
                                                       exe_func_time)  # duplicate and find dip

        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")

    list_keys = []
    func_keys_value = 0
    list_int_keys = []
    func_keys = baseutils.findkey_list(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc, list_keys)
    while func_keys != None:
        list_keys.append(func_keys)
        # print("Key > ", end='')
        # for j in range(0, len(list_keys)):
        #     for i in range(0, len(func_keys)):
        #         if str(list_keys[j][i].value()) == "True":
        #             print("1", end='')
        #         elif str(list_keys[j][i].value()) == "False":
        #             print("0", end='')
        #     print("")
        for i in range(0, len(func_keys)):
            if str(func_keys[i].value()) == "True":
                func_keys_value += pow(2, i)
        # print(func_keys_value)
        prev_len = len(baseutils.unique(list_int_keys))
        list_int_keys.append(func_keys_value)
        func_keys_value = 0
        if prev_len != len(baseutils.unique(list_int_keys)):
            print(len(baseutils.unique(list_int_keys)))
        func_keys = baseutils.findkey_list(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc,
                                      list_keys)

def ham_cks(dip_no):

    obf_bench_name = sys.argv[3]
    orig_bench_address = sys.argv[4]

    exe_func_time = 0
    exe_non_func_time = 0

    orgwires, orgpinwires, orgkeywires, orginterwires, orgpoutwires = logicwire.wire_dep(orig_bench_address)
    obfwires, obfpinwires, obfkeywires, obfinterwires, obfpoutwires = logicwire.wire_dep(obf_bench_name)

    list_dip = []
    orgcirc = [None] * len(orgpoutwires)
    str_dip = [None] * len(obfpinwires)
    list_str_dip = []
    list_orgcirc = []
    list_cpy_dip = []
    res = 1

    timeout_array = deque([20] * 10)
    const_solve = []

    iter = 0
    keyin1 = [None] * len(obfkeywires)
    keyin2 = [None] * len(obfkeywires)
    keyinc = [None] * len(obfkeywires)

    interval = math.floor(len(orgpoutwires))

    for i in range(0, len(obfkeywires)):
        keyin1[i] = Var()
        keyin1[i].symbol = obfkeywires[i].name + "_1" + str(iter)
        baseutils.h_print(DBG_PR, "keyin1", i, " ==>", keyin1[i].getSymbol())
        keyin2[i] = Var()
        keyin2[i].symbol = obfkeywires[i].name + "_2" + str(iter)
        baseutils.h_print(DBG_PR, "keyin2", i, " ==>", keyin2[i].getSymbol())
        keyinc[i] = Var()
        keyinc[i].symbol = obfkeywires[i].name + "c"
        baseutils.h_print(DBG_PR, "keyinc", i, " ==>", keyinc[i].getSymbol())

    while iter < dip_no and interval != 0:
        res, dscinp, new_func_time, interval, timeout_array, const_solve = baseutils.finddipham(obfpinwires,
                                                                                                obfkeywires,
                                                                                                obfinterwires,
                                                                                                obfpoutwires, list_dip,
                                                                                                list_orgcirc, keyin1,
                                                                                                keyin2,
                                                                                                exe_func_time, interval,
                                                                                                timeout_array,
                                                                                                const_solve)  # duplicate and find dip

        print("res > ", res)
        if res == 1:
            orgcirc = logicwire.var_log_sim(dscinp, orgwires, iter)
            iter += 1
            list_dip.append(dscinp)

            cpy_dscinp = copy.deepcopy(dscinp)
            list_cpy_dip.append(cpy_dscinp)

            for i in range(0, len(dscinp)):
                if str(dscinp[i].value()) == "True":
                    str_dip[i] = "1"
                else:
                    str_dip[i] = "0"
            list_str_dip.append(str_dip)
            str_dip = [None] * len(obfpinwires)
            list_orgcirc.append(orgcirc)

            exe_func_time = new_func_time
        elif res == -2:
            interval -= 1
            if interval == 0:
                res = -1
        elif res == -1 and interval != 0:
            interval -= 1
            res = 1
        else:
            baseutils.h_print(INF_PR, "=============================================================")
            baseutils.h_print(INF_PR, "No more DIP ------------------------------- Iterations = ", iter)
            baseutils.h_print(INF_PR, "=============================================================")
            Monosat().newSolver()

    baseutils.h_print(DBG_PR, "================ re-initializing DIPs")
    new_list_dips = Var(true())
    for i in range(0, len(list_str_dip)):
        for j in range(0, len(list_str_dip[i])):
            if list_str_dip[i][j] == "1":
                list_dip[i][j] = Var(true())
                Solve(list_dip[i][j])
            elif list_str_dip[i][j] == "0":
                list_dip[i][j] = Var(false())
                Solve(Not(list_dip[i][j]))
            new_list_dips = And(new_list_dips, list_dip[i][j])
    baseutils.h_print(DBG_PR, "================ keyFind SAT call")

    for i in range(0, len(list_dip)):
        for j in range(0, len(list_dip[i])):
            baseutils.h_print(DBG_PR, "DIP", i, "[", j, "] = ", str(list_dip[i][j].value()))
        baseutils.h_print(DBG_PR, "")

    baseutils.h_print(WAR_PR, "---------------- looking for key (Last SAT Call) ------------")

    list_keys = []
    func_keys_value = 0
    list_int_keys = []
    func_keys = baseutils.findkey_list(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc, list_keys)
    while func_keys != None:
        # print("Key > ", end='')
        # for i in range(0, len(func_keys)):
        #     if str(func_keys[i].value()) == "True":
        #         print("1", end='')
        #     elif str(func_keys[i].value()) == "False":
        #         print("0", end='')
        # print("")
        list_keys.append(func_keys)
        for i in range(0, len(func_keys)):
            if str(func_keys[i].value()) == "True":
                func_keys_value += pow(2, i)
        # print(func_keys_value)
        prev_len = len(baseutils.unique(list_int_keys))
        list_int_keys.append(func_keys_value)
        func_keys_value = 0
        if prev_len != len(baseutils.unique(list_int_keys)):
            print(len(baseutils.unique(list_int_keys)))
        func_keys = baseutils.findkey_list(obfkeywires, obfinterwires, obfpoutwires, list_dip, list_orgcirc, keyinc,
                                      list_keys)











