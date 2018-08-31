import os, sys, unicodedata
import pandas as pd

pd.set_option('display.width', 500)


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def setup(df, a_c):
    if a_c == 'Account':
        df = df.fillna('')
        df['Address'] = df['Postcode'] + ' ' + df['Street'] + ' ' + df['State'] + ' ' + df['City']
        df['Address'] = df['Address'].str.strip()
        cmap = {'South Korea': 'Korea, Republic of', 'USA': 'United States', 'US': 'United States', 'us': 'United States'
                , 'UK': 'United Kingdom', 'Netherlands': 'The Netherlands', 'NL': 'The Netherlands', 'usa': 'United States'
                , 'England': 'United Kingdom', 'Isreal': 'Israel', 'Italia': 'Italy', 'AU': 'Australia', 'JP': 'Japan'
                , 'United states': 'United States', 'Beijing City, China': 'China', 'United Kingdon': 'United Kingdom'
                , 'United Kingdpm': 'United Kingdom', 'United Arab Republic': 'United Arab Emirates',  '12525-5245': ''
                , 'United States of America': 'United States', 'Belguim': 'Belgium', 'canada': 'Canada', 'Xhina': 'China'
                , 'BRASIL': 'Brazil', 'United A': 'United Arab Emirates', 'Americas': 'United States', 'IT': 'Italy'
                , 'switzerland': 'Switzerland', 'Dubai': 'United Arab Emirates', 'Germnay': 'Germany', 'Polska': 'Poland'
                ,  'UAE': 'United Arab Emirates', 'UNITED STATES': 'United States', 'GERMANY': 'Germany', '2035': ''
                , 'Korea': 'South Korea', 'Russian Federation': 'Russia', 'UT': 'United States', 'Europe': 'Czech Republic'
                , 'Unite': 'United States', 'Sweeden': 'Sweden'}
        df['Country'] = df['Country'].replace(cmap)
        df['LastModified'] = pd.to_datetime(df['LastModified'])
        return df
    else:
        df = df.fillna('')
        df = df[['Id', 'Name', 'Email', 'AccountName', 'JobTitle']]
        return df


def clean(dfl, dfr, a_c, stem_words):
    msg_1 = 'Cleaning Data...'
    print '%s\n%s' % (msg_1, '~' * len(msg_1))
    print 'The Following Words Are Removed In The Matching Process:\n%s\n' % stem_words
    if a_c == 'Account':
        return clean_account(dfl, stem_words), clean_account(dfr, stem_words)
    elif a_c == 'Contact':
        return clean_contact(dfl, stem_words), clean_contact(dfr, stem_words)
    else:
        return sys.exit('Warning - Incorrect Analysis Type')


def clean_account(df, stem):
    punctuation = dict.fromkeys([i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P')])

    # Convert to lower case and strip punctuation
    df['NameStrip'] = df['Name'].str.lower().apply(lambda x: x.translate(punctuation) if x != '' else x)
    df['AddressStrip'] = df['Address'].str.lower().apply(lambda x: x.translate(punctuation) if x != '' else x)

    # Remove Stem Words and words of less than 2 characters
    for col in ['NameStrip', 'AddressStrip']:
        df[col] = df[col].apply(lambda x:
                                ' '.join(word for word in
                                         [w for w in x.split(' ') if len(w) > 2 and w not in stem]))
    df = df[df['AddressStrip'] != '']
    return df


def clean_contact(df, stem):
    punctuation = dict.fromkeys([i for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P')])

    # Convert to lower case and strip punctuation
    df['JobStrip'] = df['JobTitle'].str.lower().apply(lambda x: x.translate(punctuation) if x != '' else x)
    df['AccountStrip'] = df['AccountName'].str.lower().apply(lambda x: x.translate(punctuation) if x != '' else x)

    # Remove Stem Words and words of less than 2 characters
    for col in ['AccountStrip', 'JobStrip']:
        df[col] = df[col].apply(lambda x:
                                ' '.join(word for word in
                                         [w for w in x.split(' ') if len(w) > 2 and w not in stem]))

    return df




def analyse(dfl, dfr):
    msg_1 = 'Quick Data Analysis'
    print '\n%s\n%s' % (msg_1, '-' * len(msg_1))
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
    print '\n%s' % ('-' * len(msg_1))
    return None


def analysis_type():
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


def get_path(side, a_c):
    print 'Enter Path to Data Source (%s) in the following format: \n' \
          'Mac: ''/Users/<Name>/Desktop/<filename>.<extension>\n' \
          'PC: C:\Users\<Username>\Desktop\\<filename>.<extension>\n' % side
    if a_c == 'Account':
        print '### Columns Headers ###\n[Id, Name, Street, State, City, Postcode, Country, Opps, LastModified]\n'
    if a_c == 'Contact':
        print '### Columns Headers ###\n[Id, Name, Email, HomePhone, MobilePhone, OtherPhone, JobRole, JobTitle' \
              ', Street, State, City, PostCode, Country, LastModified, AccountID, AccountName, AccountCountry]\n'
    path = raw_input()
    return check_path(path, side)


def get_data(side, a_c):
    path, ext = get_path(side, a_c)
    df = pd.DataFrame(pd.read_csv(path
                                  , delimiter=ext
                                  , low_memory=False
                                  , encoding='utf-16')).drop_duplicates().reset_index(drop=True)

    if a_c == 'Account':
        cols = ['Id', 'Name', 'Street', 'State', 'City', 'Postcode', 'Country', 'Opps', 'LastModified']
    elif a_c == 'Contact':
        cols = ['Id', 'Name', 'Email', 'Homephone', 'MobilePhone', 'OtherPhone', 'JobRole', 'JobTitle', 'Street',
                'State', 'City', 'PostCode', 'Country', 'LastModified', 'AccountID', 'AccountName', 'AccountCountry']
    else:
        cols = []
    try:
        df = df[cols]
        print '...Data Read Ok!\n\nSample Data:\n', df.head(), '\n'
        return df
    except Exception, e:
        print 'Check Data Source. The Following Columns Should Exist:\n', cols
        print str(e)
        return get_data(side, a_c)