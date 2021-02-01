import sys
import os
import ursgal
import subprocess

from .msamanda_2_0_0_9695 import msamanda_2_0_0_9695 as msamanda


class msamanda_2_0_0_17442(msamanda):
    """
    MSAmanda 2_0_0_13723 UNode

    Import functions from msamanda_2_0_0_9695
    """
    META_INFO = {
        'edit_version': 1.00,
        'name': 'MSAmanda',
        'version': '2.0.0.17442',
        'release_date': None,
        'engine_type': {
            'protein_database_search_engine': True,
        },
        'input_extensions': ['.mgf'],
        'output_extensions': ['.csv'],
        'create_own_folder': True,
        'include_in_git': False,
        'distributable': False,
        'in_development': False,
        'utranslation_style': 'msamanda_style_1',
        'engine': {
            'platform_independent': {
                'arc_independent': {
                    'exe': 'MSAmanda.exe',
                    'url': '',
                    'zip_md5': '',
                },
            }
        },
        'citation': \
            'Dorfer V, Pichler P, Stranzl T, Stadlmann J, Taus T, Winkler S, ' \
            'Mechtler K. (2014) MS Amanda, a universal identification ' \
            'algorithm optimized for high accuracy tandem mass spectra.',
    }

    def __init__(self, *args, **kwargs):
        super(msamanda_2_0_0_17442, self).__init__(*args, **kwargs)
        # if sys.platform in ['win32']:
        #     self.dependencies_ok = True
        # else:
        #     try:
        #         proc = subprocess.Popen( ['mono', '-V'], stdout = subprocess.PIPE)
        #     except FileNotFoundError:
        #         print( '''
        # ERROR: MS Amanda requires Mono 3.10.0 or newer.
        # Installation: http://www.mono-project.com/download'''
        #         )
        #
        #         self.dependencies_ok = False
        pass

    def preflight( self ):
        '''
        Formatting the command line via self.params

        Settings file is created in the output folder
        and added to self.created_tmp_files (can be deleted)

        Returns:
                self.params(dict)
        '''

        translations = self.params['translations']['_grouped_by_translated_key']

        self.params['translations']['mgf_input_file'] = os.path.join(
            self.params['input_dir_path'],
            self.params['input_file']
        )

        self.params['translations']['output_file_incl_path'] = os.path.join(
            self.params['output_dir_path'],
            self.params['output_file']
        )
        self.params['translations']['data_folder'] = self.params['output_dir_path']

        # if translations['unimod_file_incl_path']['unimod_file_incl_path'] == '' :
        self.params['translations']['unimod_file_incl_path'] = os.path.join(
            os.path.dirname(__file__),
            '..',
            'resources',
            'platform_independent',
            'arc_independent',
            'ext',
            'unimod.xml'
        )

        # building command_list !
        #
        # if sys.platform in ['win32']:
        #     self.params['command_list'] = []
        # else:
        #     self.params['command_list'] = ['mono']
        self.params['command_list'] = []
        self.params['command_list'] += [
            self.exe,
            '{mgf_input_file}'.format(**self.params['translations']),
            '{database}'.format(**self.params['translations']),
            '{0}'.format( self.params['translations']['output_file_incl_path'] + '_settings.xml' ),
            '{output_file_incl_path}'.format(**self.params['translations'])
        ]
        self.created_tmp_files.append(self.params['translations']['output_file_incl_path'] + '_settings_1.xml')

        score_ions = []
        instruments_file_input = []
        for ion in [ "a", "b", "c", "x", "y", "z", "-H2O", "-NH3", "Imm", "z+1", "z+2", "INT" ]:
            if ion.lower() in self.params['translations']['score_ion_list']:
                score_ions.append( ion )
                instruments_file_input.append('''<series>{0}</series>'''.format(ion))
        instruments_file_input.append('''</setting>''')
        instruments_file_input.append('''</instruments>''')
        self.params['translations']['score_ions'] = ', '.join( score_ions )
        self.params['translations']['instruments_file_input'] = ''.join( instruments_file_input )

        print(
            '''
            [ WARNING ] precursor_mass_tolerance_plus and precursor_mass_tolerance_minus
            [ WARNING ] need to be combined for MS Amanda (use of symmetric tolerance window).
            [ WARNING ] The arithmetic mean is used.
            '''
        )
        self.params['translations']['precursor_mass_tolerance'] = (
            float(self.params['translations']['precursor_mass_tolerance_plus']) +
            float(self.params['translations']['precursor_mass_tolerance_minus'])
        ) / 2.0

        considered_charges = []
        for charge in range(
                int(self.params['translations'][ 'precursor_min_charge' ]),
                int(self.params['translations'][ 'precursor_max_charge' ]) + 1
        ):
            considered_charges.append( '+{0}'.format(charge) )
        self.params['translations']['considered_charges'] = ', '.join( considered_charges )

        if self.params['translations']['label'] == '15N':
            for aminoacid, N15_Diff in ursgal.ukb.DICT_15N_DIFF.items():
                existing = False
                for mod in self.params[ 'mods' ][ 'fix' ]:
                    if aminoacid == mod[ 'aa' ]:
                        mod[ 'mass' ] += N15_Diff
                        mod[ 'name' ] += '_15N_{0}'.format(aminoacid)
                        existing = True
                if existing == True:
                    continue
                self.params[ 'mods' ][ 'fix' ].append(
                    {
                        'pos'   : 'any',
                         'aa'   : aminoacid,
                         'name' : '15N_{0}'.format(aminoacid),
                         'mass' : N15_Diff
                    }
                )
        self.params['translations']['enzyme_name'] = self.params['enzyme']
        self.params['translations']['enzyme_cleavage'], self.params['translations']['enzyme_position'], self.params['translations']['enzyme_inhibitors'] = self.params['translations']['enzyme'].split(';')
        self.params['translations']['enzyme'] = self.params['enzyme']

        modifications = [ ]
        for t in [ 'fix', 'opt' ]:
            fix = 'false'
            if t == 'fix':
                fix = 'true'
            for mod in self.params[ 'mods' ][ t ]:
                protein = 'false'
                n_term = 'false'
                c_term = 'false'
                if '>' in mod['name']:
                    print(
                        '''
                        [ WARNING ] MS Amanda cannot deal with '>'
                        [ WARNING ] in the modification name
                        [ WARNING ] Continue without modification {0} '''.format(mod, **mod)
                        )
                    continue
                if 'Prot' in mod[ 'pos' ]:
                    protein = 'true'
                if 'N-term' in mod[ 'pos' ]:
                    n_term = 'true'
                if 'C-term' in mod[ 'pos' ]:
                    c_term = 'true'
                if '*' in mod[ 'aa' ]:
                    modifications.append( '<modification fix="{0}" protein="{1}" nterm="{2}" cterm="{3}" delta_mass="{4}">{5}</modification>'.format(
                                        fix, protein, n_term, c_term, mod[ 'mass' ], mod[ 'name' ] ))
                    continue
                modifications.append( '<modification fix="{0}" protein="{1}" nterm="{2}" cterm="{3}" delta_mass="{4}">{5}({6})</modification>'.format(
                                    fix, protein, n_term, c_term, mod[ 'mass' ], mod['name'], mod[ 'aa' ] )
                                )

        self.params['translations']['modifications'] = ''.join( modifications )

        templates = self.format_templates( )
        for file_name, content in templates.items():
            file2write = self.params['translations']['output_file_incl_path'] + file_name
            with open(
                    file2write,
                    'w'
                ) as out:
                print(content, file=out)
                self.print_info(
                    'Wrote input file {0}'.format(
                        file2write
                    ),
                    caller = 'Info'
                )
                self.created_tmp_files.append(
                    file2write
                )
        return self.params

    def format_templates( self ):
        self.params['translations']['exe_dir_path'] = os.path.dirname(self.exe)

        templates = {
            '_settings.xml' : '''<?xml version="1.0" encoding="utf-8" ?>
<settings>
    <search_settings>
        <enzyme specificity="{semi_enzyme}">{enzyme}</enzyme>
        <missed_cleavages>{max_missed_cleavages}</missed_cleavages>
        <modifications>
            {modifications}
        </modifications>
        <instrument>{score_ions}</instrument>
        <ms1_tol unit="{precursor_mass_tolerance_unit}">{precursor_mass_tolerance}</ms1_tol>
        <ms2_tol unit="{frag_mass_tolerance_unit}">{frag_mass_tolerance}</ms2_tol>
        <max_rank>{num_match_spec}</max_rank>
        <generate_decoy>{engine_internal_decoy_generation}</generate_decoy>
        <PerformDeisotoping>{deisotope_spec}</PerformDeisotoping>
        <MaxNoModifs>{max_num_per_mod}</MaxNoModifs>
        <MaxNoDynModifs>{max_num_mods}</MaxNoDynModifs>
        <MaxNumberModSites>{max_num_mod_sites}</MaxNumberModSites>
        <MaxNumberNeutralLoss>{max_num_neutral_loss}</MaxNumberNeutralLoss>
        <MaxNumberNeutralLossModifications>{max_num_neutral_loss_mod}</MaxNumberNeutralLossModifications>
        <MinimumPepLength>{min_pep_length}</MinimumPepLength>
    </search_settings>

  <basic_settings>
    <instruments_file>{output_file_incl_path}_instrument.xml</instruments_file>
    <unimod_file>{unimod_file_incl_path}</unimod_file>
    <enzyme_file>{output_file_incl_path}_enzymes.xml</enzyme_file>
    <monoisotopic>{precursor_mass_type}</monoisotopic>
    <considered_charges>{considered_charges}</considered_charges>
    <LoadedProteinsAtOnce>{batch_size}</LoadedProteinsAtOnce>
    <LoadedSpectraAtOnce>{batch_size_spectra}</LoadedSpectraAtOnce>
    <data_folder>{data_folder}</data_folder>
  </basic_settings>
</settings>
'''.format(**self.params['translations']),

        '_instrument.xml' : '''<?xml version="1.0"?>
<!-- possible values are "a", "b", "c", "x", "y", "z", "H2O", "NH3", "IMM", "z+1", "z+2", "INT" (for internal fragments) -->
<instruments>
  <setting name="{score_ions}">
{instruments_file_input}
'''.format(**self.params['translations']),

        '_enzymes.xml' : '''<?xml version="1.0" encoding="utf-8" ?>
<enzymes>
  <enzyme>
    <name>{enzyme_name}</name>
    <cleavage_sites>{enzyme_cleavage}</cleavage_sites>
    <inhibitors>{enzyme_inhibitors}</inhibitors>
    <position>{enzyme_position}</position>
  </enzyme>
</enzymes>'''.format(**self.params['translations']),
            }
        return templates