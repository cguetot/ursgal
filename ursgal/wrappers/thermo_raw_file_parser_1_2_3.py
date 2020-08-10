#!/usr/bin/env python
# import ursgal
# import os
# from collections import defaultdict as ddict
# import csv
# import sys
from .thermo_raw_file_parser_1_1_2 import thermo_raw_file_parser_1_1_2 as thermo_raw_file_parser


class thermo_raw_file_parser_1_2_3(thermo_raw_file_parser):
    """
    Unode for ThermoRawFileParser
    For further information visit
    https://github.com/compomics/ThermoRawFileParser

    Note:
        Please download ThermoRawFileParser manually from
        https://github.com/compomics/ThermoRawFileParser

    Reference:
    Hulstaert N, Sachsenberg T, Walzer M, Barsnes H, Martens L and 
    Perez-Riverol Y (2019) ThermoRawFileParser: modular, scalable and 
    cross-platform RAW file conversion. bioRxiv https://doi.org/10.1101/622852
    """

    META_INFO = {
        'edit_version': 1.00,
        'name': 'ThermoRawFileParser',
        'version': '1.1.2',
        'release_date': '2020-04-04',
        'utranslation_style': 'thermo_raw_file_parser_style_1',
        'input_extensions': ['.raw'],
        'output_extensions': ['.mzML', '.mgf', ],
        'output_suffix': None,
        'create_own_folder': False,
        'in_development': False,
        'include_in_git': False,
        'distributable': False,
        'engine_type': {
            'converter': True,
        },
        'engine': {
            'platform_independent': {
                'arc_independent': {
                    'exe': 'ThermoRawFileParser.exe',
                    'url': '',
                    'zip_md5': None,
                    'additional_exe': [],
                },
            },
        },
        'citation':
            'Hulstaert N, Sachsenberg T, Walzer M, Barsnes H, Martens L and '
            'Perez-Riverol Y (2019) ThermoRawFileParser: modular, scalable and '
            'cross-platform RAW file conversion. bioRxiv https://doi.org/10.1101/622852'
    }
