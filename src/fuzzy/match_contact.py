import pandas as pd
from record import ContactMatch
from config import find_ngrams
from fuzzywuzzy import process


def exact_contact(dfl, dfr, col1, col2, col3):
    msg_1 = 'Searching for EXACT Matches (Name & Email & Account...'
    print '%s\n%s' % (msg_1, '~'*len(msg_1))
    df_exact = pd.merge(dfl, dfr, how='inner', on=[col1, col2, col3])
    print '... %d Exact Match(es) Found!\n' % len(df_exact)
    df_exact['NameStatus'], df_exact['NameBest'], df_exact['NameProb'] = 'Exact Name', df_exact[col1], 100
    df_exact['EmailStatus'], df_exact['EmailBest'], df_exact['EmailProb'] = 'Exact Email', df_exact[col2], 100
    df_exact['AccountStatus'], df_exact['AccountBest'], df_exact['AccountProb'] = 'Exact Account', df_exact[col3], 100
    # Update LHS and RHS to exclude any exact matches
    dfl = dfl[~dfl['Id'].isin(df_exact['Id_x'])].reset_index(drop=True)
    dfr = dfr[~dfr['Id'].isin(df_exact['Id_y'])].reset_index(drop=True)

    # Format Output
    df_exact = df_exact[['Id_x', 'Id_y'
                         , col1, 'NameBest', 'NameStatus', 'NameProb'
                         , col2, 'EmailBest', 'EmailStatus', 'EmailProb'
                         , col3, 'AccountBest', 'AccountStatus', 'AccountProb']]
    df_exact.columns = ['Id_L', 'Id_R'
                        , 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
                        , 'Email_L', 'Email_R', 'EmailStatus', 'EmailProb'
                        , 'Account_L', 'Account_R', 'AccountStatus', 'AccountProb']
    return df_exact, dfl, dfr


def fuzzy_contact(debug, dfl, dfr):
    msg_1 = 'Searching for FUZZY Matches...'
    msg_2 = '(Debug Mode Active)\n' if debug else '(Debug Mode Inactive)\n'
    print '%s\n%s\n%s' % (msg_1, '~' * len(msg_1), msg_2)

    matching_records = []
    for idx, row in dfl.iterrows():
        status_i = ContactMatch('No Name', 'N/A', 0, 'No Email', 'N/A', 0
                                , 'No Account', 'N/A', 0, 'No Job', 'N/A', 0
                                , -1, 'Create New')

        print 'Searching for Matching Emails...'
        email_matches = dfr[dfr['Email'] == row.Email]

        # Exact Name Match(es) Found
        if not email_matches.empty:
            print '...%d Exact Email Match(es) Found:\n' % len(email_matches)
            print email_matches
        else:
            pass






