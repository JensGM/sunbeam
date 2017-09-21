
def create_DUMPFLUX(self, fluxnumfile_name):
    deck['RUNSPEC', 1:1, 0] = [
        ('NOSIM'),
        ('OPTIONS', [sunbeam.default * 85, 1]),
        ('OPTIONS', [sunbeam.default * 231, 1])
    ]

    deck['GRID', 1:1, 0] = [
        ('FLUXTYPE', ['PRESSURE']),
        ('DUMPFLUX'),
        ('INCLUDE', [fluxnumfile_name]),
        ('FLUXREG', [1])
    ]

    deck['PARALLEL', 0:1] = []

    deck['REGDIMS'] << lambda regdims:
        ('REGDIMS', [v if i != 3 else 1 for i, v in enumerate(regdims)])

    if 'RESTART' in deck:
        print(dedent("""\
            WARNING: DUMPFLUX file contains a RESTART.
            This may cause problems with execution of DUMPFLUX run.
            Please check the RESTART file path before you proceed!"""))

    with open(self.DUMPFLUX_name, 'w') as out:
        print(deck, file=out)
