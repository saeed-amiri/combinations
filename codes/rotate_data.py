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
        self.rotate_df(df, angle)

    def rotate_df(self,
                  df: pd.DataFrame,  # df of the atoms information: Atoms_df
                  angle: float  # Angle of the rotation in degree
                  ) -> None:
        """apply the math method and return rotated ones"""
        arr = df[['x', 'y', 'z']].to_numpy()
        print(arr[:, 0])


if __name__ == "__main__":
    data = relmp.ReadData(sys.argv[1])
    rot = Rotate(data.Atoms_df, 90)
    "rotate the data"
