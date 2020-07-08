# -*- coding: utf-8 -*-

import numpy as np



#create txt
txt = "Docker Test \n"
for board in client.list_boards():
    txt += "\n" + "Hi" + " : " + np.sum(1)+ "Docker Works" +"\n"
    t_file =  open(r"documentation/docker_test.txt", "w+")
t_file.write(txt)
t_file.close()
