import sys
import pandas as pd
import numpy as np
import read_lmp_data as relmp


class Doc:
    """rotate the pd datframe of the data around the center of mass
    of the data.
    It will rotate about y axis and counterclocwise
    input:
        Data in the DataFrame
        Angle of rotation (in degree)
    output:
        DataFrame
    """


class Rotate:
    """rotate the data along x axis counterclocwise"""
    def __init__(self,
                 df: pd.DataFrame,  # df of the atoms information: Atoms_df
                 angle: float  # Angle of the rotation in degree
                 ) -> None:
        self.df_rotated = self.rotate_df(df, angle)

    def rotate_df(self,
                  df: pd.DataFrame,  # df of the atoms information: Atoms_df
                  angle: float  # Angle of the rotation in degree
                  ) -> None:
        """apply the math method and return rotated ones"""
        arr: np.array = df[['x', 'y', 'z']].to_numpy()  # Convert data to array
        center_mass: np.array  # Ceter of mass of the data
        center_mass = self.get_com(arr)
        df[['x', 'y', 'z']] = self.y_rotation(arr, center_mass, angle)
        return df

    def y_rotation(self,
                   arr: np.array,  # xyz of the dataframe in array
                   com: np.array,  # The center of mass of the data
                   angle: float  # Angle of roatation in degree
                   ) -> np.array:
        """rotate the array around y-axis"""
        theta: float = np.radians(angle)
        rot_matrix: np.array  # Rotation matrix around y axis
        rot_matrix = np.zeros((3, 3))
        rot_matrix[0, 0] = np.cos(theta)
        rot_matrix[0, 2] = np.sin(theta)
        rot_matrix[1, 1] = 1
        rot_matrix[2, 0] = -rot_matrix[0, 2]
        rot_matrix[2, 2] = rot_matrix[0, 0]
        for i in range(3):
            arr[:, i] -= com[i]
        rot_arr: np.array = np.matmul(arr, rot_matrix)  # rotated matrix
        for i in range(3):
            rot_arr[:, i] += com[i]
        return rot_arr

    def get_com(self,
                arr: np.array  # df of the atoms information: Atoms_df
                ) -> np.array:
        """ return x, y, z of the center of mass of the dataframe as
        np.array"""
        com: np.array  # To return COM
        com = np.ones(3)
        com = [np.mean(arr[:, 0]), np.mean(arr[:, 1]), np.mean(arr[:, 2])]
        return com


if __name__ == "__main__":
    import write_lmp as lmpwrt
    data = relmp.ReadData(sys.argv[1])
    rot = Rotate(data.Atoms_df, 270)
    data.Atoms_df = rot.df_rotated
    print(data.Angles_df)
    # wrt = lmpwrt.WriteLmp(data, output='rotated.data')
    # wrt.write_lmp()
    
