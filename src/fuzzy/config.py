import os, sys
import numpy as np
import pandas as pd


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def clean(dfl, dfr, a_c, stem_words):
    print '- Step 2 -\nCleaning In Progress...'
    if a_c == 'Account':
        return clean_account(dfl, stem_words), clean_account(dfr, stem_words)
    elif a_c == 'Contact':
        return clean_contact(dfl, stem_words), clean_contact(dfr, stem_words)
    else:
        return sys.exit('Warning - Incorrect Analysis Type')


def clean_contact(df, stem):
    # Ensure all columns of type str
    df = df.astype(str)
    # Replace Null/Nan with empty str
    df = df.replace({'Null': '', 'nan': '', })
    # Dictionary mapping punctuation to spaces
    punc_map = {',': ' ', '/': ' ', '\\': ' ', ':': ' ', ';': ' ', '.': ' ', '-': ' '}
    # Apply mapping to Account/Title
    for col in ['Account', 'Title']:
        new_col = col + 'Strip'
        for k, v in punc_map.iteritems():
            df[new_col] = df[col].apply(lambda x: x.replace(k, v))
        # Convert all to lower case
        df[new_col] = df[new_col].str.lower().astype(str)
        # Convert foreign characters and remove punctuation
        df[new_col] = df[new_col].apply(lambda x: x.translate(None, string.punctuation))
        # Remove all words where len(word) < 3 and exclude stem words
        df[new_col] = df[new_col].apply(lambda x: ' '.join(i for i in [i for i in x.split(' ') if len(i) > 2 and i not in stem]))
    return df


def clean_account(df, stem):
    for i in df.columns:
        if i not in ['LastModified']:
            df[i] = df[i].astype(str)
    df['LastModified'] = pd.to_datetime(df['LastModified'])

    df = df.replace('Null', '').replace('nan', '')
    df['Country'] = df['Country'].replace('South Korea', 'Korea, Republic of').replace('USA', 'United States')
    df['NameStrip'] = df['Name'].apply(lambda x: x.replace(',', ' ').replace('/', ' ').replace('\\', ' ').replace(':', ' ').replace(';', ' ').replace('.', ' '))
    df['NameStrip'] = df['NameStrip'].str.lower().astype(str)
    df['NameStrip'] = df['NameStrip'].apply(lambda x: x.translate(None, string.punctuation))
    df['NameStrip'] = df['NameStrip'].apply(lambda x: ' '.join(i for i in [i for i in x.split(' ') if len(i) > 2 and i not in stem]))
    df['Address'] = df['PostCode'] + ' ' + df['Street'] + ' ' + df['City']
    df['Address'] = df['Address'].str.strip()
    df['AddressStrip'] = df['Address'].apply(lambda x: x.replace(',', ' ').replace('/', ' ').replace('\\', ' ').replace('\n', ' ').replace(':', ' ').replace(';', ' ').replace('.', ' '))
    df['AddressStrip'] = df['AddressStrip'].str.lower().astype(str)
    df['AddressStrip'] = df['AddressStrip'].apply(lambda x: x.translate(None, string.punctuation))
    df['AddressStrip'] = df['AddressStrip'].apply(lambda x: ' '.join(i for i in [i for i in x.split(' ') if len(i) > 2 and i not in stem]))
    df = df.replace('', np.nan)
    df.columns = ['Id', 'Name', ]
    return df


def analyse(dfl, dfr):
    print '\nQuick Data Analysis\n%s' % ('~'*20)
    if dfl.equals(dfr):
        sys.exit('Warning - Data Sources Are Exactly the Same (Re-Run Required)')
    print '- LHS -'
    print 'Records: ', len(dfl), ', Deduped: ', len(dfl.drop_duplicates()), '\nUniques: ',
    for i in dfl.columns:
        print len(pd.unique(dfl[i])), '%ss,' % i,
    print '\nNulls: ',
    for i in dfl.columns:
        print len(dfl[dfl[i].isnull()]), '%ss,' % i,
    print '\n\n- RHS -'
    print 'Records: ', len(dfr), ', Deduped: ', len(dfr.drop_duplicates()), '\nUniques: ',
    for j in dfr.columns:
        print len(pd.unique(dfr[j])), '%ss,' % j,
    print '\nNulls: ',
    for j in dfr.columns:
        print len(dfr[dfr[j].isnull()]), '%ss,' % j,
    print '\n%s' % ('~'*20)
    return None


def analysis_type():
    """

    :return:
    """
    print 'Accounts [1]\nContacts [2]'
    a_t = raw_input()
    if a_t == '1':
        return 'Account'
    elif a_t == '2':
        return 'Contact'
    else:
        print 'Please Type A Valid Integer From The Options Below!'
        return analysis_type()


def check_path(path, side):
    if os.path.isfile(path):
        ext = path[-3:]
        if ext not in ('csv', 'txt', 'tsv'):
            print 'Sorry, Only csv/tsv/txt Supported\n'
            return get_path(side)
        ext = ',' if ext == 'csv' else '\t'
        return path, ext
    else:
        print 'Path Does Not Exist, Please Type A Valid Path!'
        return get_path(side)


def get_path(side):
    print 'Use Default Data [1] or Set Manually [2]?'
    choice = raw_input()
    if choice == '1':
        if side == 'L':
            print 'Reading: /Users/JackShipway/Desktop/eu2.csv ...'
            return check_path('/Users/JackShipway/Desktop/eu2.csv', side)
        elif side == 'R':
            print 'Reading: /Users/JackShipway/Desktop/us3.csv ...'
            return check_path('/Users/JackShipway/Desktop/us3.csv', side)
    elif choice == '2':
        print 'Enter Path to Data Source (%s) in the following format: \n' \
              'Mac: ''/Users/<Name>/Desktop/<filename>.<extension>\n' \
              'PC: C:\Users\<Username>\Desktop\\<filename>.<extension>' % side
        path = raw_input()
        return check_path(path, side)
    else:
        print 'Please Type A Valid Integer From The Options Below!'
        return get_path(side)


def get_data(side, a_c):
    path, ext = get_path(side)
    df = pd.DataFrame(pd.read_csv(path, delimiter=ext, low_memory=False)).drop_duplicates().reset_index(drop=True)
    if a_c == 'Account':
        cols = ['Id', 'Name', 'Street', 'State', 'City', 'PostCode', 'Country', 'LastModified']
    else:
        cols = ['Id', 'Name', 'Email', 'HomePhone', 'MobilePhone', 'OtherPhone', 'JobRole', 'JobTitle', 'Street',
                'State', 'City', 'PostCode', 'Country', 'LastModified', 'AccountId', 'AccountName', 'AccountCountry']
    try:
        df = df[cols]
        print '...Data Read Ok!\n\nSample Data:\n', df.head()
        return df
    except Exception, e:
        print 'Check Data Source. The Following Columns Should Exist:\n', cols
        print str(e)
        return get_data(side, a_c)

