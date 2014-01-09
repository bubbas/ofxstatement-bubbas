from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
import csv


class LbbAmazonCsvStatementParser(CsvStatementParser):
    mappings = {"date": 1, "memo": 3, "amount": 6}
    date_format = "%d.%m.%Y"
    EXCHANGE_FEE_MEMO_TEXT = "AUSLANDSEINSATZENTGELT"

    def split_records(self):
        return csv.reader(self.fin, delimiter=';')

    def parse(self):
        statement = CsvStatementParser.parse(self)
        if self.merge_exchange_fee:
            # merge all records with the name AUSLANDSEINSATZENTGELT
            # into previous transaction. Ignore all lines with amount == 0.00
            last_real_transaction_id = -1
            for idx in range(len(statement.lines)):
                # we may delete stuff from this list, so check if
                # the index is ok
                if idx >= len(statement.lines):
                    break
                if statement.lines[idx].memo == self.EXCHANGE_FEE_MEMO_TEXT and last_real_transaction_id >= 0:
                    # change the real transaction
                    statement.lines[last_real_transaction_id].amount += statement.lines[idx].amount
                    # also change the memo field to note the exchange fee
                    memo_change = "({0}: {1})".format(self.EXCHANGE_FEE_MEMO_TEXT,
                                                      statement.lines[idx].amount)
                    statement.lines[last_real_transaction_id].memo += " " + memo_change
                    # delete the exchange fee transaction
                    del statement.lines[idx]
                # please note that idx may now point to the next fresh line
                if statement.lines[idx].amount:
                    last_real_transaction_id = idx
        return statement

    def parse_record(self, line):
        #Free Headerline
        if self.cur_record <= 1:
            return None

        # Empty transactions to include amazon points
        if line[6] == '':
            if self.ignore_amazon_points:
                return None
            line[6] = '0,00'
        #Change decimalsign from , to .
        line[6] = line[6].replace(',', '.')

        # fill statement line according to mappings
        sl = super(LbbAmazonCsvStatementParser, self).parse_record(line)
        return sl


class LbbAmazonPlugin(Plugin):

    def get_parser(self, fin):
        f = open(fin, "r", encoding='iso-8859-1')
        parser = LbbAmazonCsvStatementParser(f)
        parser.statement.account_id = self.settings['account']
        parser.statement.currency = self.settings['currency']
        parser.statement.bank_id = self.settings.get('bank', 'LBB_Amazon')
        parser.ignore_amazon_points = self.settings.get('ignore_amazon_points', 'false').lower() in ('true', 'yes', 'on')
        parser.merge_exchange_fee = self.settings.get('merge_exchange_fee'.lower(), 'false').lower() in ('true', 'yes', 'on')
        return parser
