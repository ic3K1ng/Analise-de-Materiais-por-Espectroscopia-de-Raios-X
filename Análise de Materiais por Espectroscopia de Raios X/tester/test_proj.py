#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIT License

Copyright (c) 2023 ajccosta

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
# Author: Andre Costa
#   changed by Vitor Duarte

"""  Test the folowing program.
     ATTENTION:
     change the program name if different from the below
"""
MY_PROG="../prog.py"


import sqlite3
from contextlib import redirect_stdout
import traceback
import os
import sys
import builtins
import subprocess

import importlib


MY_DB="spectrum.db"

use_colors = True
try:
    from colorama import Fore
    #from colorama import Style
    GREEN = Fore.GREEN
    RED = Fore.RED
    RESET = Fore.RESET
except ImportError:
    use_colors = False
    GREEN = ""
    RED = ""
    RESET = ""


def prerun( )->bool:
    """ pre check if some functions exist and are working 
    """
    return True


def findtabname(db, prefix:str)->str:
    resp = db.execute("pragma main.table_list;").fetchall()
    for t in resp:
        if t[1].lower().startswith(prefix):
            return t[1]
        
    return None
    

def chk1(db):
    resp = db.execute("pragma main.table_list;").fetchall()
    ntab=0
    tab=None
    for t in resp:
        if t[3]>=2 and t[3]<=6: 
            ntab+=1
            
    if ntab!=5:
        print("number of tables in the DB is wrong")
    else:
        print("tables created")
        
        tab = findtabname(db, "elem")
        c=db.execute("select count(*) from "+tab+";")
        print("elements:",c.fetchall())
        tab = findtabname(db, "lin")
        c=db.execute("select count(*) from "+tab+";")
        print("xlines:",c.fetchall())
        
    
def chk2(db):
    ana = findtabname(db, "anal")
    
    num, file = db.execute("select * from "+ana+";").fetchall()[0]
    if type(file)!=str and type(num)==str:
        tmp = num
        num = file
        file = tmp
    print(num, file)
    tab = findtabname(db, "resul")
    c=db.execute("select count(*) from "+tab+";")
    print("results:",c.fetchall())
    

            
            
            
def posrun(dbfile, file):
    """ run after one test (i.e. after running 'file' test)
        if needed, adapt code to the project being tested
        and to include special tests that don't just use input files
    """
    db = sqlite3.connect(dbfile, isolation_level=None)
    #db = sqlite3.connect(dbfile)
      
    if file == '1_create.txt':
        chk1(db)
            
    elif file == '2_load.txt':
        chk2(db)

    elif file == '3_summary.txt':
        pass

    elif file == '4_execute.txt':
        pass
# =============================================================================
#         with open("resultados1.txt") as f:
#             x = f.readlines()
#             x.sort()
#             for i in x:
#                 print(i.strip())
#         os.unlink("resultados1.txt")
#         with open("todos.txt") as f:
#             x = f.readlines()
#             x.sort()
#             for i in x:
#                 print(i.strip())
#         os.unlink("todos.txt")
#         with open("zeze.txt") as f:
#             x = f.readlines()
#             x.sort()
#             for i in x:
#                 print(i.strip())
#         os.unlink("zeze.txt")
# 
# =============================================================================
    db.close()



def mooshak():
    """ run the tests
    """
    orig_print = builtins.print
    orig_input = builtins.input
    python=sys.executable
    

    if not prerun():
        print(f"{RED}Can\'t continue.{RESET}")
        #os.unlink('_code.py')
        return
    #print(f"{GREEN}Passed pre-test!{RESET}")

    try: 
        os.mkdir("outs")
        os.unlink(MY_DB) 
    except:
        pass          
    passedAllTests = True

    for file in sorted(os.listdir("tests/in")):
        print("Testing tests/in/", file)
        cmd = f"{python} {MY_PROG}\n\t< tests/in/{file}\n\t> outs/out-{file}"
        print(f" running: {cmd}")

        if file == "5_graf.txt":
            print(f"{RED}CHECK IF CHART IS OK (tester can't check it). Close it.{RESET}")
            try:
                bkend=os.environ.pop("MPLBACKEND",None)
                # if spyder defines inline plots, that will not work for
                # a subprocess...
            except:
                pass
            
        with open(f"tests/in/{file}") as fin, \
            open(f"outs/out-{file}", "w") as fout:
                subprocess.run([python, MY_PROG], stdin=fin, stdout=fout )

        if file == "5_graf.txt" and bkend!=None:
            os.environ["MPLBACKEND"]=bkend
            
        print("DONE")
        diff = False

        try:
            with open(f"outs/out-{file}", "a") as f:
                with redirect_stdout(f):
                    posrun(MY_DB, file)
        except Exception as e:
            # Get exception info
            err = traceback.format_exc()
            print("ERROR:", err, end="")
            print(f"{RED} >> {e}\nFailed on test {file}{RESET}\n" )
            diff = True
            passedAllTests = False
            print('\n')
            continue

        with open(f"outs/out-{file}") as f:
            output_lines = [l.strip() for l in f.readlines()]

        expected_lines = []
        teste_out = file.replace("in", "out")  
               
        try:
            with open('tests/out/' + teste_out, "r", encoding="utf-8") as f:
                for line in f.readlines():
                    expected_lines.append(line.strip())
        except Exception as e:
            err = traceback.format_exc()
            print("ERROR:", e)
            expected_lines = []

        if len(output_lines) != len(expected_lines):
            print(f"{RED}Expecting", len(expected_lines),
                  "lines, got", len(output_lines), f"{RESET}")
            diff = True
            passedAllTests = False

        for i in range(min(len(expected_lines), len(output_lines))):
            if (output_lines[i] != expected_lines[i]):
                print(f"{i}: expecting: '{expected_lines[i]}' got: '{output_lines[i]}'")
                diff = True
                passedAllTests = False

        for i in range(min(len(expected_lines), len(output_lines)),\
                       max(len(expected_lines), len(output_lines))):
            if i >= len(expected_lines):
                print(f"{i}: -- \t got: '{output_lines[i]}'")
            else:
                print(f"{i}: expecting: '{expected_lines[i]}'")

        if not diff:
            print(f"{GREEN}Passed test!{RESET}")

        else:
            print(f"{RED}Test Failed!{RESET}")
        print("\n")

    if passedAllTests:
        print(f"{GREEN}** Passed all tests! **{RESET}")

    

    builtins.input = orig_input


###################

mooshak()
