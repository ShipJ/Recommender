import pandas as pd
from record import Record


def exact(dfl, dfr):
    exact = pd.merge(dfl, dfr, how='inner', on=['Name', 'Address', 'Country'])
    print 'There were %s Exact Matches!' % len(exact)

    # Update LHS and RHS to exclude any exact matches
    dfl = dfl[~dfl['ID'].isin(exact['ID_x'])].reset_index(drop=True)
    dfr = dfr[~dfr['ID'].isin(exact['ID_y'])].reset_index(drop=True)
    return dfl, dfr


def fuzzy(debug, dfl, dfr):
    if debug:
        print '(Debug Mode Active)\n'
    else:
        print '(Debug Mode Inactive)\n'


    for idx, row in dfl.iterrows():
        status_i = Record('No Match', 'N/A', 0, 'No Match', 'N/A', 0, -1, 'Create New')

        # All possible Matches
        rhs_i = dfr[dfr['Country'] == row.Country]

        # Check Name
        name_matches = rhs_i[rhs_i['Name'] == row.Name]
        if len(name_matches) > 0:
            print 'There were %s matches!' % len(name_matches)
            print name_matches

        # Check Address
        else:
            print 'There were no name matches. Trying Address Instead'
            address_matches = rhs_i[rhs_i['Address'] == row.Address]
            if len(address_matches) > 0:
                print 'There were %s matches!' % len(address_matches)
            else:
                pass
                # best overall?












