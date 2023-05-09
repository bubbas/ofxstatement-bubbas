from typing import Iterable

from ofxstatement.plugin import Plugin
from ofxstatement.parser import StatementParser
from ofxstatement.statement import Statement, StatementLine
from ofxstatement import statement


from PyPDF2 import PdfReader
import pandas as pd
import io
import re


class LbbAmazonPlugin(Plugin):
    """LbbAmazonPlugin to read LBB Amazon Creditcard Statements from PDF"""

    def get_parser(self, filename: str) -> "LbbAmazonPdfParser":
        parser=LbbAmazonPdfParser(filename)
        parser.statement.currency = self.settings.get('currency', 'EUR')
        parser.statement.bank_id = self.settings.get('bank', 'LBB_Amazon')
        parser.statement.account_id = self.settings.get('account', '')
        parser.statement.account_type = self.settings.get('account_type', 'CHECKING')
        parser.statement.trntype = "OTHER"
    
        return parser

class LbbAmazonPdfParser(StatementParser):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        

    def parse(self) -> Statement:
        """Main entry point for parsers

        super() implementation will call to split_records and parse_record to
        process the file.
        """
        #reader = PdfReader(self.filename)
        self.reader = PdfReader(self.filename)
        return super().parse()

    def split_records(self) -> Iterable[str]:
        """Return iterable object consisting of a line per transaction"""
        # fill text_body with text fromm all pages
        text_body = ""
        for i in range(len(self.reader.pages)):
            current_page = self.reader.pages[i]
            text_body+=current_page.extract_text()


        #text = "26.11.2022 Prime Video *1I19H8104   442-011518546LU 27.11.2022 0,99-"

        # Extract information with regexp
        date1_pattern = r'(\d{2}\.\d{2}\.\d{4})'
        purchase_pattern = r'(.*?)'
        date2_pattern = r'(?<=\s)(\d{2}\.\d{2}\.\d{4})'
        amount_pattern = r'(\d+,\d{2}[-,+])'

        purchase_regex = f"{date1_pattern}{purchase_pattern}{date2_pattern}.*?\s{amount_pattern}"


        content =[]
        
        # For each line check if matches and store to dictionary
        for line in io.StringIO(text_body):
            match = re.search(purchase_regex, line)
            if match:
                purchase_date1 = match.group(1)        
                purchase_pattern = match.group(2)
                purchase_pattern=" ".join(purchase_pattern.split())
                purchase_date2 = match.group(3)        
                amount = match.group(4)
                #print("Purchase date:", purchase_date1)
                #print("Purchase pattern:", purchase_pattern)
                #print("Exechute date:", purchase_date2)
                #print("Amount charged:", amount)
                amount=amount.replace(",",".")
                amount = float(amount[-1]+amount[:-1])        
                new_row = {'Date':purchase_date1, 'Date2':purchase_date2, 'Memo':purchase_pattern, 'Amount':amount}
                content.append(new_row)
                #lines.append(line)
            else:
                pass
        # Create pandas dataframe from dictionary        
        df = pd.DataFrame.from_dict(content)    
        df['Date']=pd.to_datetime(df['Date'],format='%d.%m.%Y')
        df['Date2']=pd.to_datetime(df['Date2'],format='%d.%m.%Y')
        return df.iterrows()        


    def parse_record(self, line: str) -> StatementLine:
        """Parse given transaction line and return StatementLine object"""
        data = line[1]
        stml = StatementLine()
        stml.date=data['Date2']
        stml.date_user=data['Date']
        stml.amount=data['Amount']
        stml.memo=data['Memo']
        stml.id = statement.generate_transaction_id(stml)
        return stml

