import sys

from config import get_data, analysis_type, analyse


if __name__ == '__main__':

    print '%s\nWelcome To Jack\'s Fuzzy Matching Algorithm!\n%s\n' % ('~'*43, '~'*43)
    print 'What Would You Like To Analyse?\n%s' % ('-'*31)
    a_c = analysis_type()

    print '\nReading Data forming the LHS...\n%s' % ('-'*31)
    dfl = get_data(side='L', a_c=a_c)
    print '\n\nReading Data forming the RHS...\n%s' % ('-'*31)
    dfr = get_data(side='R', a_c=a_c)

    analyse(dfl, dfr)
    print '\nHappy With Those Figures? [y/n]'
    response = raw_input()
    if response != 'y':
        sys.exit('Check Data Sources and Try Again.\n')

    print '\nAlgorithm Running...\n%s' % ('~' * 20)

    # STEP 4 - Loop through all LHS records
    # df_final = main_algo(dfl, dfr, a_c)