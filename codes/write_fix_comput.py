import re
import typing
import itertools
import numpy as np
import pandas as pd
from colors_text import TextColor as bcolors


class Doc:
    """write LAMMPS commands in a file name as: `setting.lmp`
    It will contains:
    Group:
        number of group will be defeind by the number of files
    Radial distutbution function:
        include copmute and fix for all the pairs in the final datafile
    Density profile:
        for each  group (i.e. each file)

    Input:
        A DataFrame contains inforamtion about atoms type and name
    Output:
        A file named: `setting.lmp`
    """
