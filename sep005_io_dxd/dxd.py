import os
from pathlib import Path
from typing import Union
import dwdatareader
import numpy as np

class Channel():
    def __init__(self, channel:dwdatareader.DWChannel, verbose=True):
        self.verbose = verbose
        self.name = channel.name
        self.sample_rate = channel.sample_rate
        self.unit = channel.unit
        self.df = channel.dataframe()
        self.time = self.df.index


    def __str__(self):
        if self.verbose:
            return f'{self.name} [{self.unit}] @ {self.sample_rate}Hz: (min:{self.min:.3f}, max:{self.max:.3f})'
        else:
            return f'{self.name}'

    @property
    def min(self):
        return self.df.min().item()

    @property
    def max(self):
        return self.df.max().item()

    @property
    def nan_samples(self):
        """
        Check if there are samples as NaN
        :return:
        """
        if len(self.df) != len(self.df.dropna()):
            raise ValueError(f'Channel {self.name} contain NaN samples')
        if self.verbose:
            print(f'QA (NaN samples) : Imported {self.name} contain no NaNs')

    @property
    def missing_samples(self):
        """
        Check if the sampling frequency is maintained properly
        :return:
        """
        # check the index matches the sampling frequency
        second_derivative = np.diff(self.time,
                                    n=2)  # Calculate the second differences between consecutive elements
        is_equidistant = np.allclose(second_derivative,
                                     0)  # Second derivative is zero for equidistant samples (skip first boundary)
        if not is_equidistant:
            raise ValueError(f'Samples missing from channel {self.name}')
        if self.verbose and is_equidistant:
            print(
                f'QA (missing samples) : Imported signal {self.name} is equidistant spaced on index'
            )

class DxdFileReader:

    """
    DXD file, reads the the file and can access trough properties

    """

    def __init__(self, filename: str, filerootfolder: str = "", qa=True, verbose=False):
        """

        :param filename:
        :param filerootfolder:
        :param qa: Run quality assurance tests,
        """
        self.filename = filename
        self.file_rootfolder = filerootfolder
        self.fullpath = filename
        self.verbose = verbose
        if filerootfolder:
            self.fullpath = os.path.join(filerootfolder, filename)

        if not os.path.isfile(self.fullpath):
            raise FileNotFoundError(f"File not Found {self.fullpath}")

        with dwdatareader.open_file(self.fullpath) as file:
            info = file.info
            self.dt = info.start_store_time
            self.fs = info.sample_rate  # This the global sampling rate
            self.duration = info.duration

            self.df = file.dataframe(channels=list(file.sync_channels))
            self.time = self.df.index.to_list()
            self.channels = [
                Channel(file[name], verbose=self.verbose) for name in file.sync_channels
            ]
            self.info = info

        if verbose:
            print(
                f'Loaded {len(self.channels)} channels starting at {self.dt} at {self.fs}Hz'
            )
            for _c in self.channels:
                print(_c)

        if qa:
            self.missing_samples
            self.nan_samples

    @property
    def nan_samples(self):
        """
        Check if there are samples as NaN
        :return:
        """
        for _c in self.channels:
            _c.nan_samples

    @property
    def missing_samples(self):
        """
        Check if the sampling frequency is maintained properly
        :return:
        """
        # check the index matches the sampling frequency
        for _c in self.channels:
            _c.missing_samples

    def to_sep005(self) -> list[dict]:
        """_summary_

        Args:

        Returns:
            list: signals
        """
        signals = []
        for chan in self.channels:
            data = chan.df.to_numpy()
            fs_signal = len(data) / self.duration

            signal = {
                'name': chan.name,
                'data': data,
                'start_timestamp': str(self.dt),
                'fs': fs_signal,
                'unit_str': chan.unit
            }
            signals.append(signal)

        return signals




def read_dxd(path: Union[str, Path], verbose=False, qa=True) -> list[dict]:
    """
    Primary function to read dxd files based on file_path

    :param

    """
    dxd_reader = DxdFileReader(path, verbose=verbose, qa=qa)

    return dxd_reader.to_sep005()