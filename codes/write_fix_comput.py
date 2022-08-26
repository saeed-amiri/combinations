import re
import typing
import itertools
import numpy as np
import pandas as pd
from colors_text import TextColor as bcolors


class Doc:
    """write LAMMPS commands in a file name as: `setting.lmp`
    if it asked in the struct file
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

class WriteGroup:
    """write groups for each file"""
    def __init__(self) -> None:
        print(f'{self.__class__.__name__}')


class WriteDistribution:
    """write commands for calculating ditribution function for all
    the pairs"""
    def __init__(self) -> None:
        print(f'{self.__class__.__name__}')


class WriteFix(WriteGroup, # Write group information
               WriteDistribution  # Write radial distribution function
               ):
    """call all the classes and write the commands"""
    def __init__(self) -> None:
        fname: str = 'setting.lmp'  # Name of the output file
        print(f'{bcolors.OKCYAN}\n{self.__class__.__name__}:\n'
              f'\tWriting: `{fname}`{bcolors.ENDC}\n')
        WriteGroup.__init__(self)
        WriteDistribution.__init__(self)