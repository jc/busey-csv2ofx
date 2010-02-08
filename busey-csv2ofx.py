#!/usr/bin/env python
# 2009-02-16
# This script takes in a Busey bank (http://busey.com) CSV export and outputs a
# OFX on standard out.
# usage:
#  python busey-csv2ofx.py Export.csv > Export.ofx

class Transaction(object):
    def __init__(self, id, date, amount, balance, description="", memo=""):
        self.id = id
        self.date = date
        self.description = description
        self.memo = memo
        self.amount = amount
        self.balance = balance
        self.type = "OTHER"
    
    def to_ofx(self):
        return """<STMTTRN>
<TRNTYPE>%s/TRNTYPE>
<DTPOSTED>%s</DTPOSTED>
<TRNAMT>%s</TRNAMT>
<FITID>%s</FITID>
<NAME>%s</NAME>
<MEMO>%s</MEMO>
</STMTTRN>""" % (self.type, format_date(self.date), self.amount,\
                     self.id, self.description, self.memo)

# Busey bank's csv export looks like (starting with a blank line):
#
#Account Name: NAME NAME NAME
#Account Number: NUMBER
#Date Range: MM/DD/YYYY - MM/DD/YY
#
#Transaction Number,Date,Description,Memo,Amount Debit,Amount Credit,Balance,Check Number,Fees
#TRANSACTION
#....
def csv_to_data(filename):
    csv = open(filename, "r")
    ln = 0
    account_id = None
    start = None
    end = None
    transactions = []
    for line in csv:
        line = line.strip()
        if line is "": 
            ln += 1
            continue
        if ln == 2:
            account_id = line.split(':')[1].strip()
        if ln > 5:
            transactions.append(csv_to_transaction(line))
        ln += 1
    start = transactions[0].date
    end = transactions[-1].date
    return transactions, account_id, start, end

def csv_to_transaction(line):
    data = line.split(',')
    debit = str_to_float(data[4])
    credit = str_to_float(data[5])
    amount = credit - debit    
    return Transaction(data[0], data[1], amount, data[6], \
                           data[2][1:-1], data[3][1:-1])

def str_to_float(number):
    if number is "": return 0.0
    else: return float(number)

def format_date(date):
    month, day, year = date.split('/')
    return "%s%s%s000000" % (year, month, day)

def transactions_to_ofx(transactions, account_id, start, end, bank_id = "071102568", account_type = "CHECKING", currency="USD"):
    ofx_preamble, ofx_header, ofx_footer = templates()
    start_date = format_date(start)
    end_date = format_date(end)
    print ofx_preamble
    print ofx_header % locals()
    balance = None
    for transaction in transactions:
        print transaction.to_ofx()
        balance = transaction.balance
    print ofx_footer % locals()

def templates():
    ofx_preamble = """OFXHEADER:100
DATA:OFXSGML
VERSION:102
SECURITY:NONE
ENCODING:USASCII
CHARSET:1252
COMPRESSION:NONE
OLDFILEUID:NONE
NEWFILEUID:NONE"""

    ofx_header = """<OFX>
<BANKMSGSRSV1>
<STMTTRNRS>
<STMTRS>
<CURDEF>%(currency)s</CURDEF>
<BANKACCTFROM>
<BANKID>%(bank_id)s</BANKID>
<ACCTID>%(account_id)s</ACCTID>
<ACCTTYPE>%(account_type)s</ACCTTYPE>
</BANKACCTFROM>
<BANKTRANLIST>
<DTSTART>%(start_date)s</DTSTART>
<DTEND>%(end_date)s</DTEND>"""
    
    ofx_footer = """</BANKTRANLIST>
<LEDGERBAL>
<BALAMT>%(balance)s</BALAMT>
<DTASOF>%(end_date)s</DTASOF>
</LEDGERBAL>
<AVAILBAL>
<BALAMT>%(balance)s</BALAMT>
<DTASOF>%(end_date)s</DTASOF>
</AVAILBAL>
</STMTRS>
</STMTTRNRS>
</BANKMSGSRSV1>
</OFX>"""

    return ofx_preamble, ofx_header, ofx_footer

if __name__ == "__main__":
    import sys
    csvfile = sys.argv[1]
    transactions, account_id, start, end = csv_to_data(csvfile)
    transactions_to_ofx(transactions, account_id, start, end)
