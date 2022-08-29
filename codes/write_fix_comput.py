from lib2to3.pgen2 import grammar
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
        self.write_group(df, f)

    def write_group(self,
                    df: pd.DataFrame,  # All atoms infos
                    f: typing.TextIO  # File to write to
                    ) -> None:
        """write the group section"""
        f.write(f'#{"Groups based on each file":.^85}\n')
        groups = self.mk_group(df)
        for k, v in groups.items():
            types: list[str] = [str(item) for item in v]
            group = k.capitalize()
            members = ' '.join(types)
            f.write(f'group {group} type {members}\n')
        f.write(f'\n')

    def mk_group(self,
                 df: pd.DataFrame  # All atoms infos
                 ) -> dict[str, list[int]]:
        """make groups based on the files"""
        groups: dict[str, list[int]]  # Retrun name of groups and types in it
        group_name: list[str] = []  # Name of the groups from file names
        fnames: list[str] = df['fname']  # Name of the files
        for name in fnames:
            try:
                g_name = name.split('.')[0]
            except IndexError:
                g_name = name
            group_name.append(g_name)
        groups = {k: [] for k in group_name}
        for _, row in df.iterrows():
            try:
                g_name = row['fname'].split('.')[0]
            except IndexError:
                g_name = row['fname']
            groups[g_name].append(row['type'])
        return groups


class WriteDistribution:
    """write commands for calculating ditribution function for all
    the pairs"""
    def __init__(self,
                 df: pd.DataFrame,  # All atoms infos
                 f: typing.TextIO  # File to write to
                 ) -> None:
        """write rdf commands"""
        self.write_rdf(df, f)

    def write_rdf(self,
                  df: pd.DataFrame,  # All atoms information
                  f: typing.TextIO
                  ) -> None:
        """give the radial distribution computations"""
        f.write(f'#{"Radial Distribution Functions":.^85}\n')
        pair_list: list[str] = self.mk_pairs(df)  # All the pairs
        NBIN: int = 1000  # Number of the rdf Nbin
        NEVERY: int = 1  # Use input values every this many timesteps
        NREPEAT: int = 1  # Number of times to use inout values for averging
        NFREQ: int = 5000  # Calculate averages every this many timesteps
        for i, item in enumerate(pair_list):
            pair = f'{item[0]}_{item[1]}'
            type0 = df.loc[df['name'] == item[0]]['type'][0]
            type1 = df.loc[df['name'] == item[1]]['type'][0]
            f.write(f'compute {pair} all rdf {NBIN} {type0} {type1}\n')
            f.write(f'fix {i:02d} all ave/time {NEVERY} {NREPEAT} {NFREQ}'
                    f' c_{pair}[*] file RDF_{pair}.txt mode vector\n')

    def mk_pairs(self,
                 df: pd.DataFrame  # All atoms information
                 ) -> list[tuple[int, int]]:
        # Make pair of all atom names
        type_list = df['name']
        pair_list = itertools.combinations_with_replacement(type_list, 2)
        return pair_list


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
        f.write(f'#{"Information from `param.json`":.^85}\n')
        df.to_csv(f, index=True, header=df.columns, sep='\t')
        f.write(f'\n')
        f.write(f'\n')

    def add_cmt(self,
                df: pd.DataFrame  # All atoms infos
                ) -> pd.DataFrame:
        """add a # as column to the df"""
        com_list: list[str]  # List contains # with size of the df
        com_list = ['#']*len(df)
        df['#'] = com_list
        df.set_index('#', inplace=True)
        return df
