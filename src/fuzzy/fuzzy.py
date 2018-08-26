import sys
from config import get_data, analysis_type, analyse
from match import fuzzy

__DEBUG__ = 0

if __name__ == '__main__':

    # Step 1 - Intro
    msg_1 = 'Welcome To Jack\'s Fuzzy Matching Algorithm!'
    print '%s\n%s\n%s\n' % ('~'*len(msg_1), msg_1, '~'*len(msg_1))
    msg_2 = 'What Would You Like To Analyse?'
    print '%s\n%s' % (msg_2, '-'*len(msg_2))

    # Step 2 - Load Data
    a_c = analysis_type()
    msg_3 = 'Reading Data forming the LHS...'
    print '\n%s\n%s' % (msg_3, '-'*len(msg_3))
    dfl = get_data(side='L', a_c=a_c)
    msg_4 = 'Reading Data forming the RHS...'
    print '\n\n%s\n%s' % (msg_4, '-'*len(msg_4))
    dfr = get_data(side='R', a_c=a_c)

    # Step 3 - Summarise Data
    analyse(dfl, dfr)
    msg_5 = 'Happy With Those Figures? [y/n]'
    print '\n%s' % msg_5
    response = raw_input()
    if response != 'y':
        sys.exit('Check Data Sources and Try Again.\n')

    # Step 4 - Remove Exact Matches



    # Step 4 - Loop through all LHS records
    df_final = fuzzy(__DEBUG__, dfl, dfr)