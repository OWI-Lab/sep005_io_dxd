import os
import numpy as np

import pytest
from sdypy_sep005.sep005 import Sep005Data

from sep005_io_dxd import read_dxd

current_dir = os.path.dirname(os.path.abspath(__file__))
static_dir = os.path.join(current_dir, 'static')
GOOD_FILES = os.listdir(os.path.join(static_dir, 'good'))


@pytest.mark.parametrize("filename", GOOD_FILES)
def test_compliance_sep005(filename):
    """
    Test the compliance with the SEP005 guidelines
    """
    file_path = os.path.join(static_dir, 'good', filename)
    signals = read_dxd(file_path)  # should already not crash here

    assert len(signals) != 0  # Not an empty response
    for sig in signals:
        Sep005Data.validate(sig) # All channels are SEP005 compliant

    for _s in signals:
        # Asserts that ZERO elements are NaN
        assert not np.isnan(_s['data']).any(), "Array contains NaN values"


def test_acc_001():
    """
    Test the correct import of a single file with acceleration data


    :return:
    """
    test_file_name = r"test_acc_001.dxd"
    file_path = os.path.join(static_dir, 'good', test_file_name)

    signals = read_dxd(file_path)

    assert len(signals) == 3
    assert all(['ACC' in s['name'] for s in signals])
    assert all([s['unit_str'] == 'g' for s in signals])
    assert all([s['fs'] == 100 for s in signals])
    assert all([len(s['data']) == 600*100 for s in signals])


def test_sg_rtd_001():
    """
    Test the correct import of a single file with a mixed sample rate data

    This file contains 12 channels, 6 strain gauges, 6 rtd channels


    :return:
    """
    test_file_name = r"test_sg_rtd_001.dxd"
    file_path = os.path.join(static_dir, 'good', test_file_name)

    signals = read_dxd(file_path)

    assert len(signals) == 12
    assert all([('SG' in s['name']) or ('RTD' in s['name']) for s in signals])
    assert all([len(s['data']) == 60*s['fs'] for s in signals])

    for _s in signals:
        if 'SG' in _s['name']:
            _s['unit_str'] = 'microstrain'
            _s['fs'] = 25

        elif 'RTD' in _s['name']:
            _s['unit_str'] = '°C'
            _s['fs'] = 10








