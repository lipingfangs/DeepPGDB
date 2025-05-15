#!/usr/bin/env python
# Copyright (C) <2020> PMBL;South China Agricultural University. All rights reserved
__author__ = "Write by Fangping Li"
__version__ = '0.1.0'

import sys
import os 
goin = sys.argv[1]
goout = sys.argv[2]

file1 = open(goin,"r")
lines = list(file1.readlines())
file2 = open("temp2020818","w")
for i in lines:
    i = i.strip()
    if i.startswith(">"):
        print("",file = file2)
        print(i,file = file2)
    else:
        print(i,end = "",file = file2)
file1.close()
file2.close()

file3 = open("temp2020818","r")
file4 = open(goout,"w")
lines = list(file3.readlines())

for i in lines[1:]:
    i = i.strip()
    print(i,file = file4)

file3.close()
file4.close()    

os.system("rm temp2020818")
