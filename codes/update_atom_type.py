import json
import typing
import numpy as np
import pandas as pd
import read_lmp_data as mlmp
from colors_text import TextColor as bcolors


class Doc:
    """update atom type for combination of data
    input a dict in the following form:
    {'A': 'decane.data', 'B: 'water.data'}
    """


class ReadParameter:
    """Update types of the atoms in the parameter file along with
    other updating the types"""
    def __init__(self, fname) -> None:
        print(f'\t{bcolors.OKCYAN}Update parameter file: '
              f'`{fname}`{bcolors.ENDC}\n')
        self.get_param(fname)

    def get_param(self, fname: str) -> None:
        with open(fname, 'r') as f:
            data = json.load(f)
        self.param = data
        del data


class UpdateType(ReadParameter):
    """updata types"""
    def __init__(self, files: dict[str, str], param_fname) -> None:
        self.files = files
        super().__init__(param_fname)
        self.check_param_files()
        self.system = self.update_atom_type()
        del files

    def check_param_files(self) -> None:
        """Check if all the files in the param are needed"""
        needed_file: list[str] = [k for _, k in self.files.items()]
        item: list[typing.Any]  # List of items in the param.json
        i_file: int  # index of the file contatins data
        for _, item in self.param.copy().items():
            for i_file, idict in enumerate(item):
                if 'file' in idict:
                    fname = idict['file']
                    if fname not in needed_file:
                        del self.param['files'][i_file]

    def update_atom_type(self) -> dict[str, dict[str, typing.Any]]:
        mass_indent: int = 0  # To increase the type of each file
        atom_indent: int = 0  # To increase the type of each file
        bond_indent: int = 0  # To increase the type of each file
        angle_indent: int = 0  # To increase the type of each file
        dihedral_indent: int = 0  # To increase the type of each file
        fname: str  # File in loop to update NOT the one in __init__!
        symbole: str  # Symbole of the file in the loop
        up_dict: dict[str, dict[str, typing.Any]] = dict()
        for i, (symbole, fname) in enumerate(self.files.items()):
            up_dict[symbole] = dict()
            up_dict[symbole]['fname'] = fname
            read_data = mlmp.ReadData(fname)
            print(f'{bcolors.OKCYAN}{self.__class__.__name__}:\n'
                  f'\tUpdating: `{fname}`{bcolors.ENDC}\n')
            read_data.Atoms_df = self.bring_to_zero(read_data.Atoms_df)
            if i == 0:
                atom_indent += read_data.NAtomTyp
                bond_indent += read_data.NBondTyp
                angle_indent += read_data.NAngleTyp
                dihedral_indent += read_data.NDihedralTyp
                mass_indent += read_data.NAtomTyp
            else:
                if read_data.NAtomTyp > 0:
                    read_data.Atoms_df = self._update_type(
                        read_data.Atoms_df, atom_indent
                        )
                    read_data.Masses_df = self._update_type(
                        read_data.Masses_df, atom_indent
                        )
                    self.update_param(symbole, atom_indent, 'atoms')
                    atom_indent += read_data.NAtomTyp
                else:
                    exit(f'{bcolors.FAIL}{self.__class__.__name__}:\n'
                         f'\tERROR: ZERO atom type in "{fname}"{bcolors.ENDC}'
                         )
                if read_data.NBondTyp > 0:
                    read_data.Bonds_df = self._update_type(
                        read_data.Bonds_df, bond_indent)
                    self.update_param(symbole, bond_indent, 'bonds')
                    bond_indent += read_data.NBondTyp
                if read_data.NAngleTyp > 0:
                    read_data.Angles_df = self._update_type(
                        read_data.Angles_df, angle_indent)
                    self.update_param(symbole, angle_indent, 'angles')
                    angle_indent += read_data.NAngleTyp
                if read_data.NDihedrals > 0:
                    read_data.Dihedrals_df = self._update_type(
                        read_data.Dihedrals_df, dihedral_indent)
                    self.update_param(symbole, dihedral_indent, 'dihedrals')
                    dihedral_indent += read_data.NDihedralTyp
            up_dict[symbole]['data'] = read_data
        return up_dict

    def update_param(self, symb: str, indent: int, parameter: str) -> None:
        """update type of atom in the parameter file"""
        for f in self.param['files']:
            if f['symb'] is symb:
                for atom in f[parameter]:
                    atom['type'] += indent

    def _update_type(self, df: pd.DataFrame, indent: int) -> pd.DataFrame:
        df['typ'] += indent
        return df

    def bring_to_zero(self, atom_df: pd.DataFrame) -> pd.DataFrame:
        """bring minimum of each block to zero in x, y, and z"""
        atom_df['x'] -= np.min(atom_df['x'])
        atom_df['y'] -= np.min(atom_df['y'])
        atom_df['z'] -= np.min(atom_df['z'])
        return atom_df
