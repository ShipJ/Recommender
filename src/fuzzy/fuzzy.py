import logging
import time
import pandas as pd
from fuzzywuzzy import process
from config import intro, load, analyse, setup, clean
from match_account import exact_account, fuzzy_account
from match_contact import exact_contact, fuzzy_contact

'''
/Users/JackShipway/Desktop/PRNG/prng.txt
/Users/JackShipway/Desktop/PRNG/clavocr.txt
'''

__DEBUG__ = 0

if __name__ == '__main__':

    if __DEBUG__:
        logging.basicConfig(filename='/fuzzy_match.log', level=logging.INFO)

    # Step 1 - Intro
    logging.info('Started Step 1 - Intro')
    intro()
    logging.info('Finished Step 1 - Intro')

    # Step 2 - Load Data
    logging.info('Started Step 2 - Data Load')
    a_c, dfl, dfr = load()
    logging.info('Finished Step 2 - Data Load')

    # Step 3 - Format Data
    logging.info('Started Step 3 - Data Setup')
    dfl = setup(dfl, a_c)
    dfr = setup(dfr, a_c)

    df_clavis = dfl.copy()
    df_clavis = df_clavis[['Id', 'Name', 'Address', 'Opps']]
    df_ocr = dfr.copy()
    df_ocr = df_ocr[['Id', 'Name', 'Address']]
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

    clav_done = df_clavis.merge(df_final, left_on='Id', right_on='Id_L', how='left')
    ocr_done = clav_done.merge(df_ocr, left_on='Id_R', right_on='Id', how='outer')

    final = ocr_done.copy()
    final.columns=['IdClavisAll', 'OriginalNameClavis', 'OriginalAddressClavis', 'ClavisOpps', 'IdClavis', 'IdOCR'
        , 'NameStripClavis', 'NameStripOCR', 'NameStatus', 'NameProb'
        , 'AddressStripClavis', 'AddressStripOCR', 'AddressStatus', 'AddressProb'
        , 'IdOCRAll', 'OriginalNameOCR', 'OriginalAddressOCR']
    final['OverallStatus'] = final['NameStatus'] + ' ' + final['AddressStatus']

    # aged_debt = pd.DataFrame(pd.read_csv('/Users/JackShipway/Desktop/FinalRun/aged_debt.txt'
    #                               , delimiter='\t'
    #                               , low_memory=False
    #                               , encoding='utf-16')).drop_duplicates().reset_index(drop=True)
    #
    # import numpy as np
    # final['IsAgedDebt'] = np.where(final['IdClavisAll'].isin(aged_debt['ID']), 1, 0)


    # df_final['Overall'] = df_final['EmailStatus'] + ' ' + df_final['NameStatus'] + ' ' + df_final['AccountStatus']

    logging.info('Finished Step 7 - Finished, and Successfully saved to csv')

    final.to_csv('/Users/JackShipway/Desktop/PRNG/results.txt', sep='\t', index=None, encoding='utf-8-sig')
