import pandas as pd
from record import AccountMatch
from config import find_ngrams
from fuzzywuzzy import process


def exact_account(dfl, dfr, col1, col2):
    msg_1 = 'Searching for EXACT Matches (Name & Address)...'
    print '%s\n%s' % (msg_1, '~' * len(msg_1))
    df_exact = pd.merge(dfl, dfr, how='inner', on=[col1, col2, 'Country'])
    print '... %d Exact Match(es) Found!\n' % len(df_exact)
    df_exact['NameStatus'], df_exact['NameBest'], df_exact['NameProb'] = 'Exact Name', df_exact[col1], 100
    df_exact['AddressStatus'], df_exact['AddressBest'], df_exact['AddressProb'] = 'Exact Address', df_exact[col2], 100

    # Update LHS and RHS to exclude any exact matches
    # dfl = dfl[~dfl['Id'].isin(df_exact['Id_x'])].reset_index(drop=True)
    # dfr = dfr[~dfr['Id'].isin(df_exact['Id_y'])].reset_index(drop=True)

    # Format Output
    df_exact = df_exact[['Id_x', 'Id_y'
        , col1, 'NameBest', 'NameStatus', 'NameProb'
        , col2, 'AddressBest', 'AddressStatus', 'AddressProb']]
    df_exact.columns = ['Id_L', 'Id_R'
        , 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
        , 'Address_L', 'Address_R', 'AddressStatus', 'AddressProb']
    return df_exact, dfl, dfr


def fuzzy_account(debug, dfl, dfr):
    msg_1 = 'Searching for FUZZY Matches...'
    msg_2 = '(Debug Mode Active)\n' if debug else '(Debug Mode Inactive)\n'
    print '%s\n%s\n%s' % (msg_1, '~' * len(msg_1), msg_2)
    dfl['NameAddress'] = dfl['NameStrip'] + ' ' + dfl['AddressStrip']
    dfr['NameAddress'] = dfr['NameStrip'] + ' ' + dfr['AddressStrip']
    matching_records = []

    for idx, row in dfl.iterrows():

        status_i = AccountMatch('No Name', 'N/A', 0, 'No Address', 'N/A', 0, -1, 'Create New')
        rhs_i = dfr[dfr['Country'] == row.Country]

        # Search for Exact Name Match
        print 'Searching For Name Matches...'
        name_matches = rhs_i[rhs_i['NameStrip'] == row.NameStrip].reset_index(drop=True)

        # Exact Name Match(es) Found
        if not name_matches.empty:
            print '...%d Exact Name Match(es) Found:\n' % len(name_matches)
            # Select Closest Address Match
            match = process.extractOne(row.AddressStrip, name_matches.AddressStrip)
            name_matches = name_matches[name_matches.AddressStrip == match[0]].reset_index(drop=True)
            status_i.update_id_action(name_matches['Id'].loc[0], 'Verify')
            status_i.toggle('Address', 'Partial Address', match[0], match[1])
            status_i.toggle('Name', 'Exact Name', name_matches['NameStrip'].loc[0], 100)

        # Exact Name Match Not Found, Search for Exact Address Match
        else:
            msg_4 = '...No Name Matches, Trying Address...'
            print '%s\n%s' % (msg_4, '-' * len(msg_4))
            address_matches = rhs_i[rhs_i['AddressStrip'] == row.AddressStrip].reset_index(drop=True)

            # Exact Address Found
            if not address_matches.empty:
                print '...%d Exact Address Match(es) Found:\n' % len(address_matches)
                # Select Closest Name Match
                match = process.extractOne(row.NameStrip, address_matches.NameStrip)
                print address_matches[address_matches.NameStrip == match[0]]
                status_i.update_id_action(address_matches[address_matches.NameStrip == match[0]]['Id'].loc[0], 'Verify')
                status_i.toggle('Name', 'Partial Name', match[0], match[1])
                status_i.toggle('Address', 'Exact Address', address_matches['AddressStrip'].loc[0], 100)

            else:
                print 'Neither Name nor Address Found: '
                trigrams = [''.join(i) for i in find_ngrams(row.NameStrip, 3)]
                trigram_matches = rhs_i[rhs_i['NameStrip'].str.contains('|'.join(trigrams), na=False)]
                if not trigram_matches.empty:
                    trigram_matches['NameAddress'] = trigram_matches['NameStrip'] + ' ' + trigram_matches[
                        'AddressStrip']
                    best_match = process.extractOne(row.NameAddress, trigram_matches['NameAddress'])
                    best = trigram_matches[trigram_matches['NameAddress'] == best_match[0]].reset_index(drop=True)
                    status_i.update_id_action(best['Id'].loc[0], 'Verify')

                    best_name = process.extractOne(row.NameStrip, trigram_matches['NameStrip'])
                    best_address = process.extractOne(row.AddressStrip, trigram_matches['AddressStrip'])
                    status_i.toggle('Name', 'Partial Name', best_name[0], best_name[1])
                    status_i.toggle('Address', 'Partial Address', best_address[0], best_address[1])
                else:
                    pass

        print row.Id, '|', row.NameStrip, '|', row.AddressStrip
        print status_i.id_best, '|', status_i.name_best, '|', status_i.address_best
        print status_i.name_status, status_i.name_prob, status_i.address_status, status_i.address_prob, '\n'
        matching_records.append([row.Id, status_i.id_best
                                    , row.NameStrip, status_i.name_best, status_i.name_status, status_i.name_prob
                                    , row.AddressStrip, status_i.address_best, status_i.address_status,
                                 status_i.address_prob])

    df = pd.DataFrame()
    df = df.append(matching_records)
    df.columns = ['Id_L', 'Id_R', 'Name_L', 'Name_R', 'NameStatus', 'NameProb', 'Address_L', 'Address_R',
                  'AddressStatus', 'AddressProb']
    return df
