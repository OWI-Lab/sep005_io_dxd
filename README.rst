SEP005 .dxd io
-----------------------

Basic package to import data collected from Dewesoft .DXD files compliant with
SDyPy format for timeseries as proposed in SEP005.

Installation
------------

Can be readily be installed from pip: ``pip install sep005-io-dxd``

Using the package
------------------

    .. code-block:: python

        from sep005_io_dxd import read_dxd

        file_path = # Path to the dxd file of interest
        signals = read_dxd(file_path)


Acknowledgements
----------------
This package was developed in the framework of the
`Interreg Smart Circular Bridge project
<https://vb.nweurope.eu/projects/project-search/smart-circular-bridge-scb-for-pedestrians-and-cyclists-in-a-circular-built-environment/>`_
