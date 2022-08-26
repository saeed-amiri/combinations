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
    def __init__(self,
                 df: pd.DataFrame,  # All atoms infos
                 f: typing.TextIO  # File to write to
                 ) -> None:
        print(f'{self.__class__.__name__}')


class WriteDistribution:
    """write commands for calculating ditribution function for all
    the pairs"""
    def __init__(self,
                 df: pd.DataFrame,  # All atoms infos
                 f: typing.TextIO  # File to write to
                 ) -> None:
        pass


class WriteFix(WriteGroup,  # Write group information
               WriteDistribution  # Write radial distribution function
               ):
    """call all the classes and write the commands"""
    def __init__(self,
                 df: pd.DataFrame  # DataFrame contains infos of all atoms
                 ) -> None:
        fname: str = 'setting.lmp'  # Name of the output file
        print(f'{bcolors.OKCYAN}\n{self.__class__.__name__}:\n'
              f'\tWriting: `{fname}`{bcolors.ENDC}\n')
        self.call_all(fname, df)

    def call_all(self,
                 fname: str,  # Name of the output file
                 df: pd.DataFrame  # All atoms infos
                 ) -> None:
        """call all the classes and functions to write commands"""
        with open(fname, 'w') as f:
            self.write_header(df, f)
            WriteGroup.__init__(self, df, f)
            WriteDistribution.__init__(self, df, f)

    def write_header(self,
                    df: pd.DataFrame,  # All atoms infos
                    f: typing.TextIO  # IO to write to
                    ) -> None:
        """write the df as a header to the file"""
        df = self.add_cmt(df)
        f.write(f'# Information from `param.json`\n')
        df.to_csv(f, index=True, header=df.columns, sep='\t')
        f.write(f'\n')
        f.write(f'\n')

    def add_cmt(self, 
                    df: pd.DataFrame  # All atoms infos
                    ) -> pd.DataFrame:
        """add a # as column to the df"""
        com_list: list[str] # List contains # with size of the df
        com_list = ['#']*len(df)
        df['#cmt'] = com_list
        df.set_index('#cmt', inplace=True)
        return df
