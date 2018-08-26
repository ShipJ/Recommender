import pandas as pd


lhs = pd.DataFrame(pd.read_csv('/Users/JackShipway/Desktop/lhs.txt', encoding='utf-16', delimiter='\t'))
rhs = pd.DataFrame(pd.read_csv('/Users/JackShipway/Desktop/rhs.txt', encoding='utf-16', delimiter='\t'))


# Get all exact matches
exact = pd.merge(lhs, rhs, how='inner', on=['Name', 'Address', 'Country'])
print 'There were %s Exact Matches!' % len(exact)

lhs = lhs[~lhs['ID'].isin(exact['ID_x'])].reset_index(drop=True)
rhs = rhs[~rhs['ID'].isin(exact['ID_y'])].reset_index(drop=True)

for idx, row in lhs.iterrows():
    status_i = Record('No Match', 'N/A', 0, 'No Match', 'N/A', 0, -1, 'Create New')

    # All possible Matches
    rhs_i = rhs[rhs['Country'] == row.Country]

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












