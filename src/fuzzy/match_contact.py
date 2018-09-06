import pandas as pd
import logging
from record import ContactMatch
from config import set_thresholds
from fuzzywuzzy import process


def exact_contact(dfl, dfr, col1, col2, col3):
    msg_1 = 'Searching for EXACT Matches (Name & Email & Account...'
    print '%s\n%s' % (msg_1, '~' * len(msg_1))
    df_exact = pd.merge(dfl, dfr, how='inner', on=[col1, col2, col3])
    print '... %d Exact Match(es) Found!\n' % len(df_exact)
    df_exact['NameStatus'], df_exact['NameBest'], df_exact['NameProb'] = 'Exact Name', df_exact[col1], 100
    df_exact['EmailStatus'], df_exact['EmailBest'], df_exact['EmailProb'] = 'Exact Email', df_exact[col2], 100
    df_exact['AccountStatus'], df_exact['AccountBest'], df_exact['AccountProb'] = 'Exact Account', df_exact[col3], 100
    df_exact = df_exact[[
        'Id_x', 'Id_y'
        , col2, 'EmailBest', 'EmailStatus', 'EmailProb'
        , col1, 'NameBest', 'NameStatus', 'NameProb'
        , col3, 'AccountBest', 'AccountStatus', 'AccountProb']]
    df_exact.columns = [
        'Id_L', 'Id_R'
        , 'Email_L', 'Email_R', 'EmailStatus', 'EmailProb'
        , 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
        , 'Account_L', 'Account_R', 'AccountStatus', 'AccountProb']
    return df_exact, dfl, dfr


def fuzzy_contact(debug, dfl, dfr):
    msg_1 = 'Searching for FUZZY Matches...'
    msg_2 = '(Debug Mode Active)\n' if debug else '(Debug Mode Inactive)\n'
    print '%s\n%s\n%s\n' % (msg_1, '~' * len(msg_1), msg_2)
    email_threshold, name_threshold, account_threshold = set_thresholds()

    matching_records = []
    for idx, row in dfl.iterrows():

        msg_3 = 'Analysing Record: '
        logging.info('%s\n%s%d' % ('-' * len(msg_3), msg_3, idx))

        # Initialise status as Create
        status_i = ContactMatch(
            'No Name', 'N/A', 0, 'No Email', 'N/A', 0
            , 'No Account', 'N/A', 0, 'No Job', 'N/A', 0
            , -1, 'Create New')

        # Email Address does not exist -
        if row.Email == '':
            logging.info('... No Email Address Found!')
            status_i.action = 'Create New - No Email'

        else:
            logging.info('Searching for Matching Emails...')
            email_matches = dfr[dfr['Email'] == row.Email].reset_index(drop=True)

            # Exact Email Match(es) Found
            if not email_matches.empty:
                msg_4 = 'Searching for Matching Names...'
                logging.info('...%d Exact Email Match(es) Found:\n%s' % (len(email_matches), msg_4))
                name_matches = process.extractOne(row.Name, email_matches['Name'])
                name_match = email_matches[email_matches['Name'] == name_matches[0]].reset_index(drop=True)

                # Exact Name Match(es) Found
                if not name_match.empty and name_matches[1] > name_threshold:

                    logging.info('...%d Exact Name Match(es) Found:\n%s' % (len(name_match), 'Searching for Matching Accounts...'))
                    account_matches = process.extractOne(row.AccountStrip, name_match['AccountStrip'])
                    account_match = name_match[name_match['AccountStrip'] == account_matches[0]].reset_index(drop=True)

                    if not account_match.empty and account_matches[1] > account_threshold:
                        logging.info('Perfect Match!')
                        status_i.update_id_action(account_match['Id'].loc[0], 'Merge')
                        status_i.toggle('Email', 'Exact Email', account_match['Email'].loc[0], 100)
                        status_i.toggle('Name', 'Exact Name', account_match['Name'].loc[0], 100)
                        status_i.toggle('Account', 'Exact Account', account_match['AccountStrip'].loc[0], 100)

                    else:
                        logging.info('Account Did Not Match!')
                        status_i.update_id_action(account_match['Id'].loc[0], 'Verify Account Name')
                        status_i.toggle('Email', 'Exact Email', name_match['Email'].loc[0], 100)
                        status_i.toggle('Name', 'Exact Name', name_match['Name'].loc[0], 100)
                        status_i.toggle('Account', 'Partial Account', account_matches[0], account_matches[1])
                else:
                    logging.info('...Name did not Match!\nChecking Account Name...')
                    account_matches = process.extractOne(row.AccountStrip, email_matches['AccountStrip'])
                    account_match = email_matches[email_matches['AccountStrip'] == account_matches[0]].reset_index(
                        drop=True)

                    if not account_match.empty and account_matches[1] > account_threshold:
                        logging.info('Perfect Match!')
                        status_i.update_id_action(-1, 'Create New - Parent Email')
                    else:
                        logging.info('Account and Name did not Match!')
                        status_i.update_id_action(-1, 'Create New - But Email Exists')
            else:
                logging.info('...No Matching Emails Found\nSearching for Matching Names...')
                name_matches = dfr[dfr['Name'] == row.Name].reset_index(drop=True)
                if not name_matches.empty:
                    logging.info('...Name Matches Found!\nChecking Email Similarity...')
                    email_match = process.extractOne(row.Email, name_matches['Email'])
                    email_matches = name_matches[name_matches['Email'] == email_match[0]].reset_index(drop=True)
                    if email_match[1] > email_threshold:
                        logging.info('...Email Similarity Ok!')
                        status_i.update_id_action(email_matches['Id'].loc[0], 'Merge')
                        status_i.toggle('Email', 'Partial Email', email_match[0], email_match[1])
                        status_i.toggle('Name', 'Exact Name', email_matches['Name'].loc[0], 100)

                        account_match = process.extractOne(row.AccountStrip, email_matches['AccountStrip'])
                        if account_match[1] == 100:
                            status_i.toggle('Name', 'Exact Name', email_matches['AccountStrip'].loc[0], 100)
                        else:
                            status_i.toggle('Name', 'Partial Account', account_match[0], account_match[1])
                    else:
                        logging.info('...Email not Similar!')
                else:
                    logging.info('...No Name Matches Found. Create New.')

        print '\nSummary'
        print row.Id, '|', row.Name, '|', row.Email, '|', row.AccountStrip
        print status_i.id_best, '|', status_i.name_best, '|', status_i.email_best, '|', status_i.account_best
        print status_i.name_status, status_i.name_prob, status_i.email_status, status_i.email_prob \
            , status_i.account_status, status_i.account_prob, status_i.action
        print '-' * len(msg_3), '\n'
        matching_records.append([
            row.Id, status_i.id_best, row.Email, status_i.email_best, status_i.email_status, status_i.email_prob
            , row.Name, status_i.name_best, status_i.name_status, status_i.name_prob
            , row.AccountStrip, status_i.account_best, status_i.account_status, status_i.account_prob])
    df = pd.DataFrame()
    df = df.append(matching_records)
    df.columns = [
        'Id_L', 'Id_R', 'Email_L', 'Email_R', 'EmailStatus', 'EmailProb', 'Name_L', 'Name_R', 'NameStatus', 'NameProb'
        , 'Account_L', 'Account_R', 'AccountStatus', 'AccountProb']
    return df
