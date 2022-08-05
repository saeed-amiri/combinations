import os
import re
import sys
import typing
from colors_text import TextColor as bcolors


class Structure:
    """read the struct file"""
    def __init__(self) -> None:
        self.fname: str = sys.argv[1]
        self.mk_block()

    def mk_block(self) -> None:
        """make a matrix out of the blocks symbols"""
        self.check_files(self.fname)
        print(f'{bcolors.OKCYAN}{self.__class__.__name__}:\n'
              f'\tReading `{self.fname}`{bcolors.ENDC}')
        self.files, self.block, self.axis, self.param_fname, self.output =\
            self.read_struct()

    def read_struct(self) -> tuple[dict, dict, dict, str, str]:
        """read the strut file"""
        f: typing.IO  # a string to save file
        line: str  # a string to save lines of the strcut file
        out_fname: str = 'blocked.data'  # Ouput file if not given in struct
        bed_count: int = 0  # to count lines in the matrix of bolcks
        symbole_dict: dict[str, str] = {}  # dict to save name and symb
        block_dict: dict[int, list[str]] = {}  # dict to save matrix
        axis_dict: dict[str, str] = dict()  # to save the second stacking axis

        with open(self.fname, 'r') as f:
            while True:
                line = f.readline()
                if line.strip().startswith('#'):
                    pass
                elif line.strip().startswith('!'):
                    sym, fname = self.get_files(line.strip())
                    symbole_dict[sym] = fname
                elif line.startswith('axis'):
                    axis_dict['axis'] = self.get_axis(line)
                elif line.startswith('param'):
                    param_fname = self.get_name(line)
                elif line.startswith('output'):
                    out_fname = self.get_name(line)
                elif line.strip():
                    m_list = self.get_matrix(line.strip())
                    block_dict[bed_count] = m_list
                    bed_count += 1
                if not line:
                    break
        self.check_file_exist(symbole_dict, block_dict)
        symbole_dict = self.check_file_need(symbole_dict, block_dict)
        # print(symbole_dict)
        return symbole_dict, block_dict, axis_dict, param_fname, out_fname

    def get_files(self, line: str) -> tuple[str, str]:
        """check the files name and if they are not empty"""
        # Drop ! from beginning
        line = re.sub('!', '', line)
        # Remove white spaces
        line = re.sub(r'\s+', '', line)
        sym, fname = line.split("=")
        self.check_files(fname)
        return sym, fname

    def check_files(self, fname: str) -> None:
        """check if the fname exist and not empty"""
        if not os.path.isfile(fname):
            exit(f'{self.__class__.__name__}:\n'
                 f'\tERROR: "{fname}" does not exist!!\n')
        if not os.path.getsize(fname) > 0:
            exit(f'{self.__class__.__name__}:\n'
                 f'\tERROR: "{fname}" is empty!!\n')

    def get_axis(self, line: str) -> str:
        """return the second stacking axis"""
        line = re.sub(r'\s+', '', line)
        ax = line.split('=')[1]
        if ax == 'z' or ax == 'y':
            return ax
        else:
            print(f'\tWARNING: Unknonwn second axis. Set to "z" ')
            ax = 'z'
            return ax

    def get_name(self, line: str) -> str:
        """return the name of the parameter files"""
        return line.split('=')[1].strip()

    def get_matrix(self, line: str) -> list[str]:
        """read the matrix section of the struct file"""
        _sym_mat: list[str]  # A list to return sequence in line
        if ' ' in line:
            print(f'{self.__class__.__name__}:\n'
                  f'\t"{bcolors.WARNING}{self.fname}" -> WARRNING: '
                  f'whitespace in the in line: '
                  f'"{line}", it is removed!{bcolors.ENDC}\n')
            line = re.sub(r'\s+', '', line)
        _sym_mat = [item for item in line]
        return _sym_mat

    def check_file_exist(self,
                         sym: dict[str, str],
                         block: dict[int, list[str]]) -> None:
        """check if all the symbols have a file defeind with them"""
        e_flag: bool = False  # To check all the typo in the input file
        for _, row in block.items():
            for i in range(len(row)):
                if row[i].isalpha():
                    if not row[i] in sym.keys():
                        print(f'{bcolors.FAIL}{self.__class__.__name__}:\n'
                              f'\tERROR: "{self.fname}" -> symbole "{row[i]}"'
                              f' is not defined{bcolors.ENDC}\n')
                        e_flag = True
                elif row[i] not in ['-', '_', '|']:
                    print(f'{bcolors.FAIL}{self.__class__.__name__}:\n'
                          f'\tERROR: "{self.fname}" -> symbole "{row[i]}" is '
                          f'not defined{bcolors.ENDC}\n')
                    e_flag = True
        if e_flag:
            exit(f'{bcolors.FAIL}Mistake(s) in the "{self.fname}"'
                 f'{bcolors.ENDC}')

    def check_file_need(self,
                        sym: dict[str, str],
                        block: dict[int, list[str]]) -> dict[str, str]:
        """check if the all the files  are needed for the structure
           if not remove it from the dict (=sys)
        """
        symbole: str  # Symbole of each data file
        for symbole, _ in sym.copy().items():
            needed: bool = False
            for _, item in block.items():
                if symbole in item:
                    needed = True
                    break
            if not needed:
                del sym[symbole]
        return sym


if __name__ == "__main__":
    super_str = Structure()
    print(super_str.axis)
