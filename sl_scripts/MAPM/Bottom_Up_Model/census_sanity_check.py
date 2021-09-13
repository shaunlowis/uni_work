import pandas as pd
import numpy as np

fp = '/home/shaun/Documents/work_dir/bottom_up/census_data/MB_plus_census_wood.xlsx'


def main(meshblock_number):
    """ Function for computing the total emissions of a meshblock, from the meshblock ID in the ECAN census data.
        By meshblock ID, the number value in the AU2013 column is expected.
    :param meshblock_number: The ID of the meshblock, this should be an integer. See the census data AU2013 column.
    """
    data = pd.read_excel(fp)
    mesh_keys = data['AU2013'].values
    np.where(mesh_keys == '590701')
    emissions = data['Emissions (grams Pm2.5) per night'].values
    emissions_mesh = emissions[np.where(mesh_keys == meshblock_number)]
    print(f'The total emissions for meshblock {meshblock_number} is: {sum(emissions_mesh)} in g/kg')


main(590701)
