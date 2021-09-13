import logging
from os.path import join

from bdbp.grid import Grid
from bdbp.utils.calc_zonal_means import MMZM
from bdbp.utils.filter import filter_mmzm
from packages.bdbp_freeze.bdbp.utils.intemediate import PREPARED, CORRECTED
from bs.core import env, util

# List of source files used to generate the monthly mean zonal mean
INPUT_SOURCES = ['SAGE_II_V7', 'HALOE_V19', 'ILAS-I_V6', 'ILAS-II_V3', 'POAM-II_V6', 'POAM-III_V4', 'MLS_V4', 'SONDE_', 'SAGE_I_v6.1']
OUTPUT_PATH = env.projects('/Projects/BDBP_new/Database/')
DATABASE_TYPE_META = {
    PREPARED: {
        'output_path': env.projects('/Projects/BDBP_new/Database/version_0/'),
        'comment': '0: prepared satellite data with no bias correction',
    },
    CORRECTED: {
        'output_path': env.projects('/Projects/BDBP_new/Database/version_1/'),
        'comment': '1: satellite data combined with bias correction'
    }
}

logger = logging.getLogger('calc_mmzm')


VERT_STRS = {
    'press': 'PRS',
    'gph': 'GPH'
}


def run(args):
    """
    Convert the arguments so that they can be used by the MMZM calculation
    :param args:
    :return:
    """
    vert_coord = args.vertical
    variable = args.variable
    database_type = args.type
    input_path = args.input_path
    output_path = args.output_path or DATABASE_TYPE_META[database_type]['output_path']
    sources = args.sources
    file_prefix = args.file_prefix

    # If only one source is provided include that in the file prefix
    if len(sources) == 1:
        s = sources[0]
        s = s[:s.rfind('_')]

        if file_prefix is not None:
            file_prefix = '{}_{}'.format(args.file_prefix, s)
        else:
            file_prefix = s

    # Prepare the output file name
    fname_prefix = "BSVerticalOzone_"
    if file_prefix is not None:
        fname_prefix = fname_prefix + file_prefix + '_'
    vstr = 'MR' if variable == 'vmr' else 'ND'
    corr_str = 'uncorr' if database_type == 0 else 'corr'

    output_fname = join(output_path, fname_prefix + '{}_{}_{}_Tier0.0_v1.0.nc'.format(vstr, VERT_STRS[vert_coord], corr_str))
    comment = DATABASE_TYPE_META[database_type]['comment']
    year_range = args.start_year, args.end_year

    logger.info('Vertical dimension: {}'.format(vert_coord))
    logger.info('Variable: {}'.format(variable))
    logger.info('Database Type: {}'.format(database_type))
    logger.info('Sources: {}'.format(sources))
    if input_path:
        logger.info('Input directory: {}'.format(input_path))
    logger.info('Output file: {}'.format(output_fname))
    logger.info('Year Range: {}'.format(year_range))

    if args.level is not None:
        logging.info('Only running for level: {}'.format(args.level))

    # Generate new corrected dataset
    grid = Grid(vert_coord, 'O3_' + variable)  # TODO: remove the 'O3_' part
    calc_mmzm(grid, database_type, output_fname, sources, year_range, comment, args.level)


def calc_mmzm(grid, database_type, output_fname, sources, year_range, comment, level=None):
    mm = MMZM(grid, database_type, year_range[0], year_range[1], sources)

    if level is not None:
        mm.level_idxs = [mm.level_idxs[level]]
    zm_array, zm_err_array, zm_corr_array, stsb = mm.calculate_mmzm()

    logger.info('Target output file: {}'.format(output_fname))
    mm.write_to_netcdf(output_fname, zm_array, zm_err_array, zm_corr_array, stsb, version_str=comment)
    logger.info('Filtering output')
    filter_mmzm(output_fname)


def process_args():
    import argparse
    parser = argparse.ArgumentParser(prog='calc_mmzm',
                                     description="Calculate monthly mean zonal means from the vertozone database")
    parser.add_argument('-v', '--vertical',
                        default='press',
                        choices=['gph', 'press', 'theta', 'wrt_tropH'],
                        help='Vertical dimension to correct'
                        )
    parser.add_argument('--variable',
                        default='vmr',
                        choices=['vmr', 'nd'],
                        help='Ozone variable to correct'
                        )
    parser.add_argument('-t', '--type',
                        default=CORRECTED,
                        choices=[PREPARED, CORRECTED],
                        type=int,
                        help='Type of the database to generate'
                        )
    parser.add_argument('-s', "--sources", type=str, metavar='',
                        default='all',
                        help="List of satellites to be plotted. Separate by comas and no spaces." \
                             " Keyword 'all' selects all satellites")
    parser.add_argument('--no-merge',
                        action='store_true',
                        help='If True, then one output file will be produced for each target satellite, rather than a single merged record')
    parser.add_argument('--start-year',
                        default=1979,
                        type=int,
                        help='Vertical dimension to correct'
                        )
    parser.add_argument('--end-year',
                        default=2016,
                        type=int,
                        help='Vertical dimension to correct'
                        )
    parser.add_argument('--input-path',
                        help='Override the default input path which depends on the database type'
                        )
    parser.add_argument('--output-path',
                        help='Override the default output path which depends on the database type'
                        )
    parser.add_argument('--file-prefix', help='Custom string which is included in the output filename')
    parser.add_argument('-l', '--level', type=int, help='Run a single selected level rather than all')
    args = parser.parse_args()

    args.sources = args.sources.upper().replace(" ", "").split(',')
    if args.sources == ['ALL']:
        args.sources = INPUT_SOURCES

    return args


def main():
    util.setup_logging()
    _args = process_args()
    logger.info('Beginning to generate MMZMs')

    if _args.no_merge:
        all_sources = _args.sources
        old_prefix = _args.file_prefix
        logger.info('Complete source list: {}'.format(all_sources))
        logger.info('Processing each source separately')
        # Iterate over each source separately
        for source in all_sources:
            # Update the sources and file prefix for this particular run
            _args.sources = [source]
            _args.file_prefix = old_prefix
            run(_args)
    else:
        run(_args)


if __name__ == '__main__':
    main()
