#!/usr/bin/env python
from __future__ import print_function
from textwrap import dedent
import os
import sunbeam

class DataFile(object):
    def __init__(self, datafile_name):
        """
        Collects the name of the root datafile.
        """
        self.datafile_name = datafile_name
        self.datafile_shortname = os.path.basename(self.datafile_name)
        self.datafile_dirname = os.path.dirname(os.path.abspath(self.datafile_name))

        self.DUMPFLUX_name = "Empty"
        self.USEFLUX_name = "Empty"

        self.recovery=('PARSE_MISSING_INCLUDE', sunbeam.action.ignore)
        self.keywords=[ # Keywords extensions for keywords not supported by OPM-PARSER
            {
                # No documentation, inaccurate definition of keyword
                "name" : "TBLKFAI4", "sections" : [ "RUNSPEC", "GRID", "EDIT", "PROPS", "REGIONS", "SOLUTION", "SUMMARY", "SCHEDULE" ],
                "data" : { "value_type" : "DOUBLE" }
            },
            {
                "name" : "GCONSUMP", "sections" : ["SCHEDULE"], "items" : [
                    { "name" : "GROUP_NAME",           "value_type" : "STRING" },
                    { "name" : "GAS_CONSUMPTION_RATE", "value_type" : "DOUBLE", "default" : 0.0 },
                    { "name" : "GAS_IMPORT_RATE",      "value_type" : "DOUBLE", "default" : 0.0 },
                    { "name" : "NODE_NAME",            "value_type" : "STRING", "default" : "NO-NODES" }
                ]
            },
            {
                "name" : "GCONSALE", "sections" : ["SCHEDULE"], "items" : [
                    { "name" : "GROUP_NAME",              "value_type" : "STRING" },
                    { "name" : "SALES_PROD_RATE_TAR",     "value_type" : "DOUBLE", "default" : 0.0 },
                    { "name" : "MAX_SALES_PROD_RATE",     "value_type" : "DOUBLE", "default" :  1.0E20 },
                    { "name" : "MIN_SALES_PROD_RATE",     "value_type" : "DOUBLE", "default" : -1.0E20 },
                    { "name" : "EXCEEDING_MAX_PROCEDURE", "value_type" : "STRING", "default" : "NONE" },
                ]
            },
            {
                "name" : "UDQ", "sections" : ["SCHEDULE"], "items" : [
                    { "name" : "OP", "value_type" : "STRING", "size_type" : "ALL" }
                ]
            },
            {
                "name" : "GCONTOL", "sections" : ["SCHEDULE"], "size" : 1, "items" : [
                    { "name" : "TOLERANCE",   "value_type" : "DOUBLE", "default" : 1.0E20 },
                    { "name" : "NUPCOL",      "value_type" : "DOUBLE", "default" : 0.0 }, # Should default to unchanged
                    { "name" : "OPERATOR",    "value_type" : "DOUBLE", "default" : 1.0E-3 },
                    { "name" : "VALUE",       "value_type" : "INT",     "default" : 5 }
                ]
            },
            {
                "name" : "WLIFTOPT", "sections" : ["SCHEDULE"], "items" : [
                    { "name" : "WELL_NAME",                     "value_type" : "STRING" },
                    { "name" : "OPTIMISE_LIFT_GAS_INJECTION_RATE", "value_type" : "STRING" },
                    { "name" : "MAX_LIFT_GAS_INJECTION_RATE_1", "value_type" : "DOUBLE", "default" : 1.0E20 }, # Default: the largest ALQ value in the well's VFP table (if Item 2 is YES). Remain unchanged (if item to is NO).
                    { "name" : "WEIGHTING_FACTOR_FOR_LIFT_GAS", "value_type" : "DOUBLE", "default" : 1.0 },
                    { "name" : "MAX_LIFT_GAS_INJECTION_RATE_2", "value_type" : "DOUBLE", "default" : 0.0 },
                    { "name" : "INCREMENTAL_GAS_RATE_WEIGHTING_FACTOR", "value_type" : "DOUBLE", "default" : 0.0 },
                    { "name" : "ADDITIONAL_LIFT_GAS","value_type" : "STRING", "default" : 'NO' }
                ]
            }
        ]
        self.deck = sunbeam.parse_deck(datafile_name,
                                       recovery=self.recovery,
                                       keywords=self.keywords)

    def check_DUMPFLUX_kw(self): return 'DUMPFLUX' in self.deck
    def  check_USEFLUX_kw(self): return  'USEFLUX' in self.deck

    def create_DUMPFLUX(self, fluxnumfile_name):
        """
        Writes a DATA file with DUMPFLUX keyword.

        Also includes NOSIM and OPTION entries for EOR functionality.

        @fluxnumfile_name : Name of the FLUXNUM kw file to be included
        """
        l = []
        for kw in self.deck:
            if kw.name == 'RUNSPEC':
                l.extend([kw, dedent("""\
                    NOSIM

                    OPTIONS
                      85* 1 /

                    OPTIONS
                      231* 1 /
                """)])
            elif kw.name == 'PARALLEL':
                l.append('--' + str(kw).replace('\n', '\n--') + '\n')
            elif kw.name == 'REGDIMS':
                l.append( kw.name )
                l.append( '  ' + ' '.join(map(str,
                    [item[0] if i != 3 else 1 for i, item in enumerate(kw[0])]
                )) + ' /\n' )
            elif kw.name == 'GRID':
                l.extend([ kw, dedent("""\
                    FLUXTYPE
                      'PRESSURE' /

                    DUMPFLUX

                    INCLUDE
                      '{}' /

                    FLUXREG
                      1 /
                """).format(fluxnumfile_name)])
            else:
                if kw.name == "RESTART":
                    print(dedent("""\
                        WARNING: DUMPFLUX file contains a RESTART.
                        This may cause problems with execution of DUMPFLUX run.
                        Please check the RESTART file path before you proceed!"""))
                l.append(kw)
        self.DUMPFLUX_name = "DUMPFLUX_"+self.datafile_shortname
        with open(self.DUMPFLUX_name, 'w') as out:
            out.writelines(map(lambda s: str(s)+'\n' , l))

    def run_DUMPFLUX_NOSIM(self, version="2014.2"):
        """
        Executes interactive ECLIPSE run with DUMPFLUX DATA file.

        ECLIPSE version 2014.2.

        Checks for errors in the output PRT file
        """

        if self.DUMPFLUX_name == "Empty":
            # l.append "ERROR: DUMPFLUX file not found or run"
            sys.exit(1)

    def run_DUMPFLUX_NOSIM_v2013(self):
        pass

    def create_USEFLUX(self, fluxnumfile_name, fluxfile_name):
        """
        Creates a USEFLUX DATA file containing the sector simulation and
        populated boundary conditions.

        @fluxnumfile_name : Name of file containing FLUXNUM kw
        @fluxfile_name : Name of FLUX file populated from full field RESTART data
        """
        l = []
        for kw in self.deck:
            if kw.name == 'REGDIMS':
                l.append( kw.name )
                l.append( '  ' + ' '.join(map(str,
                    [item[0] if i != 3 else 1 for i, item in enumerate(kw[0])]
                )) + ' /\n' )
            elif kw.name == 'RUNSPEC':
                l.extend([kw, dedent("""\
                    OPTIONS
                      85* 1 /

                    OPTIONS
                      231* 1 /
                """)])
            elif kw.name == 'NOSIM' or kw.name == 'PARALLEL':
                l.append('--' + str(kw).replace('\n', '\n--') + '\n')
            elif kw.name == 'GRID':
                l.extend([ kw, dedent("""\
                    FLUXTYPE
                      'PRESSURE' /

                    USEFLUX
                      '{}' /

                    INCLUDE
                      '{}' /

                    FLUXREG
                      1 /
                """).format(fluxfile_name, fluxnumfile_name) ])
            elif kw.name == 'SOLUTION':
                l.extend([ kw, dedent("""\
                    -- *** NOTIFICATION ***
                    -- If DUMPFLUX run is based on a RESTART
                    -- USEFLUX run needs to be run based on the DUMPFLUX run
                    -- Use the following and remove any equilibrations
                    -- RESTART
                    --   '{}' /
                """).format(self.DUMPFLUX_name.split(".")[0]) ])

        self.USEFLUX_name = "USEFLUX_"+self.datafile_shortname
        with open(self.USEFLUX_name, 'w') as out:
            out.writelines(map(lambda s: str(s)+'\n' , l))

    def add_USEFLUX_header_coarse(self, args):
        pass

    def add_USEFLUX_header_refined(self, args):
        pass


    def create_dummy_lgr_GRID_include(self, file_name, args, dummy_lgr_cells=(),
                                      dummy_lgr_wells=(), dummy_lgr_names=()):
        pass


    def write_dummy_lgr_header(self, outfile):
        pass

    def write_dummy_lgr_data(self,
                             dummy_lgr_cells,
                             dummy_lgr_wells,
                             dummy_lgr_names):
        pass

if __name__ == '__main__':
    df = DataFile('/private/jegm/ert-statoil/testdata/gen_flux/FF12_2014A_RE1_PRED15_POLYMER.DATA')
    df.create_DUMPFLUX('/private/jegm/ert-statoil/testdata/gen_flux/FLUXNUM_KW_TEST.grdecl')
    df.create_USEFLUX('/private/jegm/ert-statoil/testdata/gen_flux/FLUXNUM_KW_TEST.grdecl', 'FLUXFILE_QUESTION_MARK')
