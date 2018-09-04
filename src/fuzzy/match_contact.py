import pandas as pd
from record import ContactMatch
from config import find_ngrams
from fuzzywuzzy import process


def exact_contact(dfl, dfr, col1, col2, col3):
    msg_1 = 'Searching for EXACT Matches (Name & Email & Account...'
    print '%s\n%s' % (msg_1, '~' * len(msg_1))
    df_exact = pd.merge(dfl, dfr, how='inner', on=[col1, col2, col3])
    print '... %d Exact Match(es) Found!\n' % len(df_exact)
    df_exact['NameStatus'], df_exact['NameBest'], df_exact['NameProb'] = 'Exact Name', df_exact[col1], 100
    df_exact['EmailStatus'], df_exact['EmailBest'], df_exact['EmailProb'] = 'Exact Email', df_exact[col2], 100
    df_exact['AccountStatus'], df_exact['AccountBest'], df_exact['AccountProb'] = 'Exact Account', df_exact[col3], 100

    # Update LHS and RHS to exclude any exact matches - optimisation step only
    # dfl = dfl[~dfl['Id'].isin(df_exact['Id_x'])].reset_index(drop=True)
    # dfr = dfr[~dfr['Id'].isin(df_exact['Id_y'])].reset_index(drop=True)

    # Format Output
    df_exact = df_exact[[
        'Id_x', 'Id_y'
        , col1, 'NameBest', 'NameStatus', 'NameProb'
        , col2, 'EmailBest', 'EmailStatus', 'EmailProb'
        , col3, 'AccountBest', 'AccountStatus', 'AccountProb']]
    #
    df_exact.columns = [
        'Id_L', 'Id_R'
        , 'Email_L', 'Email_R', 'EmailStatus', 'EmailProb'
        , 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
        , 'Account_L', 'Account_R', 'AccountStatus', 'AccountProb']

    return df_exact, dfl, dfr


def fuzzy_contact(debug, dfl, dfr):

    # /Users/JackShipway/Desktop/Latest/test_1.txt
    # /Users/JackShipway/Desktop/Latest/OCRContacts.txt


    msg_1 = 'Searching for FUZZY Matches...'
    msg_2 = '(Debug Mode Active)\n' if debug else '(Debug Mode Inactive)\n'
    print '%s\n%s\n%s' % (msg_1, '~' * len(msg_1), msg_2)

    name_threshold = 95
    account_threshold = 90

    # Store successive Record objects
    matching_records = []

    for idx, row in dfl.iterrows():

        msg_3 = 'Analysing Record: '
        print '%s%d\n%s' % (msg_3, idx, '-'*len(msg_3))

        # Initialise status as Create
        status_i = ContactMatch(
            'No Name', 'N/A', 0, 'No Email', 'N/A', 0
            , 'No Account', 'N/A', 0, 'No Job', 'N/A', 0
            , -1, 'Create New')

        # Email Address does not exist -
        if row.Email == '':
            print '... No Email Address Found!'
            status_i.action = 'Create New - No Email'

        else:
            print 'Searching for Matching Emails...'
            email_matches = dfr[dfr['Email'] == row.Email].reset_index(drop=True)
            print email_matches

            # Exact Email Match(es) Found
            if not email_matches.empty:
                msg_4 = 'Searching for Matching Names...'
                print '...%d Exact Email Match(es) Found:\n%s' % (len(email_matches), msg_4)
                name_matches = process.extractOne(row.Name, email_matches['Name'])
                name_match = email_matches[email_matches['Name'] == name_matches[0]].reset_index(drop=True)
                print name_match

                # Exact Name Match(es) Found
                if not name_match.empty and name_matches[1] > name_threshold:

                    print '...%d Exact Name Match(es) Found:' % len(name_match)
                    print 'Searching for Matching Accounts...'
                    account_matches = process.extractOne(row.AccountStrip, name_match['AccountStrip'])
                    account_match = name_match[name_match['AccountStrip'] == account_matches[0]].reset_index(drop=True)
                    print account_match

                    if not account_match.empty and account_matches[1] > account_threshold:
                        print 'Perfect Match!'
                        status_i.update_id_action(account_match['Id'].loc[0], 'Merge')
                        status_i.toggle('Email', 'Exact Email', account_match['Email'].loc[0], 100)
                        status_i.toggle('Name', 'Exact Name', account_match['Name'].loc[0], 100)
                        status_i.toggle('Account', 'Exact Account', account_match['AccountStrip'].loc[0], 100)

                    else:
                        print 'Account Did Not Match!'
                        status_i.update_id_action(account_match['Id'].loc[0], 'Verify Account Name')
                        status_i.toggle('Email', 'Exact Email', name_match['Email'].loc[0], 100)
                        status_i.toggle('Name', 'Exact Name', name_match['Name'].loc[0], 100)
                        status_i.toggle('Account', 'Partial Account', account_matches[0], account_matches[1])
                else:
                    print '...Name did not Match!\nChecking Account Name...'
                    account_matches = process.extractOne(row.AccountStrip, email_matches['AccountStrip'])
                    account_match = email_matches[email_matches['AccountStrip'] == account_matches[0]].reset_index(drop=True)
                    print account_match

                    if not account_match.empty and account_matches[1] > account_threshold:
                        print 'Perfect Match!'
                        status_i.update_id_action(-1, 'Create New - Parent Email')
                    else:
                        print 'Account and Name did not Match!'
                        status_i.update_id_action(-1, 'Create New - But Email Exists')
            else:
                pass

        print '\nSummary'
        print row.Id, '|', row.Name, '|', row.Email, '|', row.AccountStrip
        print status_i.id_best, '|', status_i.name_best, '|', status_i.email_best, '|', status_i.account_best
        print status_i.name_status, status_i.name_prob, status_i.email_status, status_i.email_prob \
            , status_i.account_status, status_i.account_prob, status_i.action
        print '-'*len(msg_3), '\n'
        matching_records.append([row.Id, status_i.id_best
                                    , row.Email, status_i.email_best, status_i.email_status, status_i.email_prob
                                    , row.Name, status_i.name_best, status_i.name_status, status_i.name_prob
                                    , row.AccountStrip, status_i.account_best, status_i.account_status, status_i.account_prob
                                 ])
    df = pd.DataFrame()
    df = df.append(matching_records)
    df.columns = [
        'Id_L', 'Id_R'
        , 'Email_L', 'Email_R', 'EmailStatus', 'EmailProb'
        , 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
        , 'Account_L', 'Account_R', 'AccountStatus', 'AccountProb']
    return df
