import logging
import time
import pandas as pd
from config import intro, load, analyse, setup, clean
from match_account import exact_account, fuzzy_account
from match_contact import exact_contact, fuzzy_contact

'''
/Users/JackShipway/Desktop/Latest/OCRContacts.txt
/Users/JackShipway/Desktop/Latest/ClavisContacts.txt
'''

__DEBUG__ = 1

if __name__ == '__main__':

    if __DEBUG__:
        logging.basicConfig(filename='/Users/JackShipway/Desktop/contacts_log.log', level=logging.INFO)

    # Step 1 - Intro
    logging.info('Started Step 1 - Intro')
    a_c = intro()
    logging.info('Finished Step 1 - Intro')

    # Step 2 - Load Data
    logging.info('Started Step 2 - Data Load')
    dfl, dfr = load()
    logging.info('Finished Step 2 - Data Load')

    # Step 3 - Format Data
    logging.info('Started Step 3 - Data Setup')
    dfl = setup(dfl, a_c)
    dfr = setup(dfr, a_c)
    logging.info('Finished Step 3 - Data Setup')

    # Step 4 - Summarise Data
    logging.info('Started Step 4 - Data Summary')
    analyse(dfl, dfr)
    logging.info('Finished Step 4 - Data Summary')

    # Step 5 - Clean Name/Address Fields
    logging.info('Started Step 5 - Data Clean')
    dfl, dfr = clean(dfl, dfr, a_c)
    logging.info('Finished Step 5 - Data Clean')

    # Step 6 - Remove Exact Matches
    logging.info('Started Step 6 - Exact Matches')
    if a_c == 'Account':
        df_exact_clean, dfl, dfr = exact_account(dfl, dfr, col1='NameStrip', col2='AddressStrip')
        df_final = fuzzy_account(__DEBUG__, dfl, dfr)
    else:
        df_exact_clean, dfl, dfr = exact_contact(dfl, dfr, col1='Name', col2='Email', col3='AccountStrip')
        df_final = fuzzy_contact(__DEBUG__, dfl, dfr)
    logging.info('Finished Step 6 - Exact Matches')
    logging.info('Found %d Exact Matches: ' % len(df_exact_clean))
    logging.info(df_exact_clean)

    logging.info('Started Step 7 - Processing Final Data Set')
    df_final = pd.DataFrame(pd.concat([df_exact_clean, df_final]))
    df_final['Overall'] = df_final['EmailStatus'] + ' ' + df_final['NameStatus'] + ' ' + df_final['AccountStatus']
    logging.info('Finished Step 7 - Finished, and Successfully saved to csv')

    # df_final.to_csv('/Users/JackShipway/Desktop/Latest/results_1.txt', sep='\t', index=None, encoding='utf-16')
