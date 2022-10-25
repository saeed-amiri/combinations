import re
import numpy as np
import pandas as pd
from colors_text import TextColor as bcolors
import rotate_data as rotdf


class Doc:
    """stack atom in Z loop
    first in x and then in y or z direction"""


class UpdateAtom:
    """put atoms side to side"""
    def __init__(self,
                 block: pd.DataFrame,  # Block information
                 axis: dict[str, str],  # the second stacking axis
                 bs: dict[str, dict[str, str]]  # Inforamtion for all systems
                 ) -> None:

        self.block = block
        self.bs = bs
        self.axis = axis
        self.VACUME: int = 3  # Space between blocks
        self.stack_atoms()
        del block, bs, axis

    def stack_atoms(self) -> None:
        """stack atoms along axises"""
        print(f'{bcolors.OKCYAN}{self.__class__.__name__}:\n'
              f'\tUpdating: Atoms\n'
              f'\tSecond stacking axis: {self.axis["axis"]}{bcolors.ENDC}\n')
        row_list = self.stack_x()
        self.stack_rows(row_list)

    def stack_x(self) -> list[pd.DataFrame]:
        """stack atoms with updating id of atoms and also mol number
        this function stack data along x-axis"""
        # Declear variables
        col: int      # Column of the block data in struct file
        row: int      # Row of the block data in struct file
        v: list[str]  # List of symbols of the data file
        item: str     # An item of v
        raw_df: pd.DataFrame  # A Dataframe to keep all the row made DF
        row_list: list[pd.DataFrame] = []  # A list to keep the raws DF
        _df: pd.DataFrame  # Temperary dataframe

        x_indent: float = 0.0  # Shift in x column based on previous block
        max_x: float = 0  # max in x column after updating DataFrame
        max_id: int = 0   # max of id column after updating DataFrame
        max_mol: int = 0  # max of mol column after updating DataFrame
        for row, (_, v) in enumerate(self.block.items()):
            df_list: list[pd.DataFrame] = []  # To append DataFrames
            for col, item in enumerate(v):
                lett_dig: list[str] = re.split('(\d+)', item)  # letter&digit
                lett_dig = [item for item in lett_dig if item]
                if len(lett_dig) == 1:
                    chiz: str = lett_dig[0]  # Symbol of the file
                    _df = self.bs.system[chiz]['data'].Atoms_df.copy()
                elif len(lett_dig) == 2:
                    chiz = str(lett_dig[0])
                    angle: float = float(lett_dig[1])  # Angle for rotation
                    temp_df = self.bs.system[chiz]['data'].Atoms_df.copy()
                    rot = rotdf.Rotate(temp_df, angle)
                    _df = rot.df_rotated
                else:
                    exit(f'{bcolors.FAIL}\tError! Wrong symbol: '
                         f'{item}\n{bcolors.ENDC}')
                if col == 0:
                    df_list.append(_df)
                    max_x = np.max(_df['x'])
                    max_id = np.max(_df['atom_id'])
                    max_mol = np.max(_df['mol'])
                    del _df
                else:
                    x_indent = max_x + self.VACUME
                    _df['x'] += x_indent
                    _df['atom_id'] += max_id
                    _df['mol'] += max_mol
                    max_x = np.max(_df['x'])
                    max_id = np.max(_df['atom_id'])
                    max_mol = np.max(_df['mol'])
                    df_list.append(_df)
                    del _df
            raw_df = pd.concat(df_list, ignore_index=True, axis=0)
            row_list.append(raw_df)
            del raw_df, df_list
        return row_list

    def stack_rows(self, row_list: list[pd.DataFrame]) -> None:
        """stack atoms with updating id of atoms and also mol number
        this function stack data from self.stack_atoms along y-axis"""
        # Declear variables
        max_z: float = 0  # max in z column after updating DataFrame
        y_indent: float = 0  # Shift in y column based on previous block
        z_indent: float = 0  # Shift in z column based on previous block
        x_ave_center: float  # x of center_of_mass of bottom layer
        y_ave_center: float  # y of center_of_mass of bottom layer
        x_ave: float  # x center_of_mass of each layer
        y_ave: float  # y center_of_mass of each layer
        self.Atoms_df: pd.DataFrame  # To return data
        ax: str = self.axis['axis']  # Second stacking axis
        for i, item in enumerate(row_list):
            if i == 0:
                max_id = np.max(item['atom_id'])
                max_mol = np.max(item['mol'])
                max_z = np.max(item['z'])
                max_y = np.max(item['y'])
                x_ave_center = 0.5*(np.max(item['x'] - np.min(item['x'])))
                y_ave_center = 0.5*(np.max(item['y'] - np.min(item['y'])))
                z_ave_center = 0.5*(np.max(item['z'] - np.min(item['z'])))
            else:
                if ax == 'y':
                    y_indent = max_y + self.VACUME
                    item['y'] += y_indent
                elif ax == 'z':
                    z_indent = max_z + self.VACUME
                    item['z'] += z_indent
                item['mol'] += max_mol
                item['atom_id'] += max_id
                max_id = np.max(item['atom_id'])
                max_mol = np.max(item['mol'])
                max_y = np.max(item['y'])
                max_z = np.max(item['z'])
                x_ave = 0.5*(np.max(item['x'] - np.min(item['x'])))
                item['x'] -= (x_ave-x_ave_center)
                if ax == 'z':
                    y_ave = 0.5*(np.max(item['y'] - np.min(item['y'])))
                    item['y'] -= (y_ave-y_ave_center)
                if ax == 'y':
                    z_ave = 0.5*(np.max(item['z'] - np.min(item['z'])))
                    item['z'] -= (z_ave-z_ave_center)
        self.Atoms_df = pd.concat(row_list, ignore_index=True,  axis=0)
        self.Atoms_df.sort_values(by=['atom_id'], axis=0, inplace=True)
        del row_list


class UpdateBond:
    """updating bonds dataframe in and stack them in one DataFrame"""
    def __init__(self,
                 block: pd.DataFrame,  # Block information
                 bs: dict[str, dict[str, str]]  # Inforamtion for all systems
                 ) -> None:
        self.block = block
        self.bs = bs
        self.update_bonds()
        del bs, block

    def update_bonds(self):
        _df: pd.DataFrame  # A temprarry df to store them
        df_list: list[pd.DataFrame] = []  # To append all the DFs
        prev_natoms: int = 0  # Number of atoms up to current
        prev_nbonds: int = 0  # Number of bonds up to current
        row: int  # counting the rows, not used here just for clairity
        col: int  # counting the cols, not used here just for clairity
        for row, (_, v) in enumerate(self.block.items()):
            for col, item in enumerate(v):
                # break down to list to separate digits, in case
                chiz: str
                chiz = re.split('(\d+)', item)[0]
                try:
                    _df = self.bs.system[chiz]['data'].Bonds_df.copy()
                    prev_nbonds += self.bs.system[chiz]['data'].NBonds
                    _df['ai'] += prev_natoms
                    _df['aj'] += prev_natoms
                    df_list.append(_df)
                    del _df
                except KeyError:
                    pass
                prev_natoms += self.bs.system[chiz]['data'].NAtoms
        self.Bonds_df = pd.concat(df_list, ignore_index=True,  axis=0)
        self.Bonds_df.index += 1
        if prev_nbonds != len(self.Bonds_df):
            exit(f'\t{bcolors.FAIL}ERROR!: Problem in number of bonds\n'
                 f'\tnumber of total bonds: {prev_nbonds}'
                 f' != {len(self.Bonds_df)} number of calculated bonds'
                 f'{bcolors.ENDC}')
        del df_list


class UpdateAngle:
    """updating angles dataframe in and stack them in one DataFrame"""
    def __init__(self,
                 block: pd.DataFrame,  # Block information
                 bs: dict[str, dict[str, str]]  # Inforamtion for all systems
                 ) -> None:
        self.block = block
        self.bs = bs
        self.update_angles()
        del bs, block

    def update_angles(self):
        _df: pd.DataFrame  # A temprarry df to store them
        df_list: list[pd.DataFrame] = []  # To append all the DFs
        prev_natoms: int = 0  # Number of atoms up to current
        prev_nangles: int = 0  # Number of angles up to current
        row: int  # counting the rows, not used here just for clairity
        col: int  # counting the cols, not used here just for clairity
        for row, (_, v) in enumerate(self.block.items()):
            for col, item in enumerate(v):
                # break down to list to separate digits, in case
                chiz: str
                chiz = re.split('(\d+)', item)[0]
                try:
                    _df = self.bs.system[chiz]['data'].Angles_df.copy()
                    prev_nangles += self.bs.system[chiz]['data'].NAngles
                    _df['ai'] += prev_natoms
                    _df['aj'] += prev_natoms
                    _df['ak'] += prev_natoms
                    df_list.append(_df)
                    del _df
                except KeyError:
                    pass
                prev_natoms += self.bs.system[chiz]['data'].NAtoms
        try:
            self.Angles_df = pd.concat(df_list, ignore_index=True,  axis=0)
            self.Angles_df.index += 1
            if prev_nangles != len(self.Angles_df):
                exit(f'\t{bcolors.FAIL}ERROR!: Problem in number of angles\n'
                     f'\tnumber of total angles: {prev_nangles}'
                     f' != {len(self.Angles_df)} number of calculated angles'
                     f'{bcolors.ENDC}')
        except ValueError:
            self.Angles_df = pd.DataFrame(df_list)
            print(f'\t{bcolors.WARNING}WARNING: There is no angles defined\n'
                  f'{bcolors.ENDC}')
        del df_list


class UpdateDihedral:
    """updating dihedrals dataframe in and stack them in one DataFrame"""
    def __init__(self,
                 block: pd.DataFrame,  # Block information
                 bs: dict[str, dict[str, str]]  # Inforamtion for all systems
                 ) -> None:
        self.block = block
        self.bs = bs
        self.update_dihedrals()
        del bs, block

    def update_dihedrals(self):
        _df: pd.DataFrame  # A temprarry df to store them
        df_list: list[pd.DataFrame] = []  # To append all the DFs
        prev_natoms: int = 0  # Number of atoms up to current
        prev_ndihedrals: int = 0  # Number of angles up to current
        row: int  # counting the rows, not used here just for clairity
        col: int  # counting the cols, not used here just for clairity
        for row, (_, v) in enumerate(self.block.items()):
            for col, item in enumerate(v):
                # break down to list to separate digits, in case
                chiz: str
                chiz = re.split('(\d+)', item)[0]
                try:
                    _df = self.bs.system[chiz]['data'].Dihedrals_df.copy()
                    prev_ndihedrals += self.bs.system[chiz]['data'].NDihedrals
                    _df['ai'] += prev_natoms
                    _df['aj'] += prev_natoms
                    _df['ak'] += prev_natoms
                    _df['ah'] += prev_natoms
                    df_list.append(_df)
                    del _df
                except KeyError:
                    pass
                prev_natoms += self.bs.system[chiz]['data'].NAtoms
        try:
            self.Dihedrals_df = pd.concat(df_list, ignore_index=True,  axis=0)
            self.Dihedrals_df.index += 1

            if prev_ndihedrals != len(self.Dihedrals_df):
                exit(f'\t{bcolors.FAIL}ERROR!: Problem in number of dihedrals'
                     f'\n\tnumber of total dihedrals: {prev_ndihedrals}'
                     f' != {len(self.Dihedrals_df)}'
                     f' number of calculated dihedral{bcolors.ENDC}')
        except ValueError:
            self.Dihedrals_df = pd.DataFrame(df_list)
            print(f'\t{bcolors.WARNING}WARNING: There is no dihedral defined\n'
                  f'{bcolors.ENDC}')
        del df_list


class UpdateMass:
    """update mass section"""
    def __init__(self,
                 bs: dict[str, dict[str, str]]
                 ) -> None:
        self.bs = bs
        del bs
        self.update_mass()

    def update_mass(self) -> None:
        """append mass DataFrames"""
        _df: pd.DataFrame
        df_list: list[pd.DataFrame] = []
        for fname in self.bs.files:
            _df = self.bs.system[fname]['data'].Masses_df
            df_list.append(_df)
            del _df
        self.Masses_df = pd.concat(df_list, ignore_index=True, axis=0)
        del df_list


class UpdateVelocity:
    """update velocities of the atoms
    Update the index of the atoms"""
    def __init__(self,
                 block: pd.DataFrame,  # Block information
                 bs: dict[str, dict[str, str]]
                 ) -> None:
        self.bs = bs
        self.block = block
        del bs, block
        self.update_velocity()

    def update_velocity(self) -> None:
        """update velocity DataFrame"""
        max_id: int = 0   # max of id column after updating DataFrame
        df_list: list[pd.DataFrame] = []  # list velcoities
        for row, (_, v) in enumerate(self.block.items()):
            for col, item in enumerate(v):
                # break down to list to separate digits, in case
                chiz: str
                chiz = re.split('(\d+)', item)[0]
                _df = self.bs.system[chiz]['data'].Velocities_df.copy()
                if _df.empty:
                    print(f'\t{bcolors.WARNING}WARNING: No `Velocity` section '
                          f'for item `{chiz}`, it set to zero{bcolors.ENDC}\n'
                          )
                    _df = self.mk_velocity_df(chiz)
                if row == 0 and col == 0:
                    max_id = np.max(_df.index)
                    df_list.append(_df)
                    del _df
                else:
                    _df.index += max_id
                    max_id = np.max(_df.index)
                    df_list.append(_df)
                    del _df
        self.Velocities_df = pd.concat(df_list, axis=0)
        self.Velocities_df.sort_index(axis=0, inplace=True)

    def mk_velocity_df(self,
                       item: str  # Symbole for the file
                       ) -> pd.DataFrame:
        """return a zero data frame for the file"""
        natoms: int = self.bs.system[item]['data'].NAtoms  # Number of atoms
        velocity_arr: np.array = np.zeros((natoms, 3))  # Array with zeros
        df: pd.DataFrame  # to return
        df = pd.DataFrame(velocity_arr, columns=['vx', 'vy', 'vz'])
        df.index += 1
        del velocity_arr
        return df


class StackData(UpdateAtom,
                UpdateBond,
                UpdateAngle,
                UpdateDihedral,
                UpdateVelocity,
                UpdateMass
                ):
    """stack all the DataFrame together"""
    def __init__(self,
                 block: pd.DataFrame,
                 axis: dict[str, str],
                 bs: dict[str, dict[str, str]]
                 ) -> None:
        UpdateAtom.__init__(self, block, axis, bs)
        UpdateBond.__init__(self, block, bs)
        UpdateAngle.__init__(self, block, bs)
        UpdateDihedral.__init__(self, block, bs)
        UpdateVelocity.__init__(self, block, bs)
        UpdateMass.__init__(self, bs)
        self.update_names()
        del block, bs

    def update_names(self) -> None:
        """append name of each counterpart"""
        if not self.Bonds_df.empty:
            self.get_bond_names(self.Bonds_df)
        if not self.Angles_df.empty:
            self.get_angle_names(self.Angles_df)
        if not self.Dihedrals_df.empty:
            self.get_dihedral_names(self.Dihedrals_df)

    def get_bond_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """add columns for atoms types of each coplus"""
        ai_name: str  # Atoms name
        aj_name: str  # Atoms name
        name: list[str] = []  # List of the bonds participents
        cmt_list: list[str] = []  # List of "#"
        i_id: int  # To temp save the atoms type
        j_id: int  # To temp save the atoms type
        for ai, aj in zip(df['ai'], df['aj']):
            i_id = self.Atoms_df.iloc[ai-1]['typ']
            j_id = self.Atoms_df.iloc[aj-1]['typ']
            ai_name = self.Masses_df.iloc[i_id-1]['name']
            aj_name = self.Masses_df.iloc[j_id-1]['name']
            name.append(f'{ai_name}-{aj_name}')
            cmt_list.append('#')
        self.Bonds_df['cmt'] = cmt_list
        self.Bonds_df['name'] = name
        del name, cmt_list

    def get_angle_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """add columns for atoms types of each triples"""
        ai_name: str  # Atoms name
        aj_name: str  # Atoms name
        ak_name: str  # Atoms name
        name: list[str] = []  # List of the angles participents
        cmt_list: list[str] = []  # List of "#"
        i_id: int  # To temp save the atoms type
        j_id: int  # To temp save the atoms type
        k_id: int  # To temp save the atoms type
        for ai, aj, ak in zip(df['ai'], df['aj'], df['ak']):
            i_id = self.Atoms_df.iloc[ai-1]['typ']
            j_id = self.Atoms_df.iloc[aj-1]['typ']
            k_id = self.Atoms_df.iloc[ak-1]['typ']
            ai_name = self.Masses_df.iloc[i_id-1]['name']
            aj_name = self.Masses_df.iloc[j_id-1]['name']
            ak_name = self.Masses_df.iloc[k_id-1]['name']
            name.append(f'{ai_name}-{aj_name}-{ak_name}')
            cmt_list.append('#')
        self.Angles_df['cmt'] = cmt_list
        self.Angles_df['name'] = name
        del name, cmt_list

    def get_dihedral_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """add columns for atoms types of each quadrapels"""
        ai_name: str  # Atoms name
        aj_name: str  # Atoms name
        ak_name: str  # Atoms name
        ah_name: str  # Atoms name
        name: list[str] = []  # List of the dihedrals participents
        cmt_list: list[str] = []  # List of "#"
        i_id: int  # To temp save the atoms type
        j_id: int  # To temp save the atoms type
        k_id: int  # To temp save the atoms type
        h_id: int  # To temp save the atoms type
        for ai, aj, ak, ah in zip(df['ai'], df['aj'], df['ak'], df['ah']):
            i_id = self.Atoms_df.iloc[ai-1]['typ']
            j_id = self.Atoms_df.iloc[aj-1]['typ']
            k_id = self.Atoms_df.iloc[ak-1]['typ']
            h_id = self.Atoms_df.iloc[ah-1]['typ']
            ai_name = self.Masses_df.iloc[i_id-1]['name']
            aj_name = self.Masses_df.iloc[j_id-1]['name']
            ak_name = self.Masses_df.iloc[k_id-1]['name']
            ah_name = self.Masses_df.iloc[h_id-1]['name']
            name.append(f'{ai_name}-{aj_name}-{ak_name}-{ah_name}')
            cmt_list.append('#')
        self.Dihedrals_df['cmt'] = cmt_list
        self.Dihedrals_df['name'] = name
        del name, cmt_list
