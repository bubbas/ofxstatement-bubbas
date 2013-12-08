from ofxstatement.parser import CsvStatementParser
from ofxstatement.plugin import Plugin
from ofxstatement import statement
import csv
import re


class FlatexCsvStatementParser(CsvStatementParser):
    mappings = {"date": 0,"memo": 4, "amount": 5}
    date_format = "%d.%m.%Y"

    def split_records(self):
        return csv.reader(self.fin, delimiter=';')
 
    def parse_record(self, line):
        #Lines with no information
        if self.cur_record <= 1:
            return None
        
        if self.statement.currency==None:
            self.statement.currency=line[6]

        #Change decimalsign from , to .
        line[5]=line[5].replace('.','').replace(',','.')
            
        # fill statement line according to mappings
        sl = super(FlatexCsvStatementParser, self).parse_record(line)
        return sl    


class FlatexPlugin(Plugin):
    name = "flatex"
    def get_parser(self, fin):
        f = open(fin, "r",encoding='iso-8859-1')
        parser=FlatexCsvStatementParser(f)
        parser.statement.account_id = self.settings['account']
        parser.statement.currency = None
        parser.statement.bank_id = self.settings.get('bank', 'FLATEX_Cash') 
        return parser

