import doctest

from ofxstatement.plugins.flatex import FlatexCsvStatementParser

def doctest_FlatexCsvStatementParser():
    """Test FlatexCsvStatementParser

    Open sample csv to parse
        >>> import os
        >>> csvfile = os.path.join(os.path.dirname(__file__),
        ...                        'samples', 'flatex.csv')

    Create parser object and parse:
        >>> fin = open(csvfile, 'r', encoding='iso-8859-1')
        >>> parser = FlatexCsvStatementParser(fin)
        >>> statement = parser.parse()

    Check what we've got:
        >>> statement.account_id
        >>> len(statement.lines)
        12
        >>> statement.start_balance
        >>> statement.start_date
        >>> statement.end_balance
        >>> statement.end_date
        >>> statement.currency
        'EUR'

    Check first line
        >>> l = statement.lines[0]
        >>> l.amount
        Decimal('-1672.50')
        >>> l.payee 
        >>> l.memo
        'AusfÃ¼hrung ORDER Kauf,CNE1000004Y2 12345678,TA-Nr.: 12345678'
        >>> l.date
        datetime.datetime(2015, 4, 7, 0, 0)

    Check one more line:
        >>> l=statement.lines[2]
        >>> l.amount
        Decimal('-13.49')
        >>> l.payee
        >>> l.memo
        'GebÃ¼hren Ordernummer,12345678 Transnr 12345678,TA-Nr.: 12345678'
        >>> l.date
        datetime.datetime(2015, 4, 8, 0, 0)

    Check one more line with slashes in memo:
        >>> l=statement.lines[8]
        >>> l.amount
        Decimal('8.55')
        >>> l.memo
        'ErtrÃ¤gnisausschÃ¼ttung,LU0136412771,TA-Nr.: 12345678'
        >>> l.date
        datetime.datetime(2015, 4, 9, 0, 0)
              
    """

def test_suite(*args):
    return doctest.DocTestSuite(optionflags=(doctest.NORMALIZE_WHITESPACE|
                                             doctest.ELLIPSIS|
                                             doctest.REPORT_ONLY_FIRST_FAILURE|
                                             doctest.REPORT_NDIFF
                                             ))
load_tests = test_suite

if __name__ == "__main__":
    doctest.testmod()

