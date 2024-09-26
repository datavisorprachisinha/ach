import json 
import pandas as pd
import argparse

parser = argparse.ArgumentParser(description="Process some arguments.")

parser.add_argument('-i', '--inputFile', type=str, help='input NACHA')
parser.add_argument('-o', '--outputFile', type=str, help='output CSV')

args = parser.parse_args()

file_path = args.inputFile
out_path = args.outputFile

with open(file_path) as f:
    data = json.load(f)
  

'''
four high level groups in JSON of interest
IATBatches
NotificationOfChange
ReturnEntries
batches

3 types of addenda observed: addenda05 (additional payment info), addenda98 (notification of change), addenda99 (return)
category: Forward, Return, NOC
'''

'''
from batchControl: nothing
from batchHeader: ODFIIdentification, companyIdentification, companyEntryDescription, companyName, effectiveEntryDate, originatorStatusCode, serviceClassCode, settlementDate, standardEntryClassCode
from entryDetails (list of entry dicts): DFIAccountNumber, RDFIIdentification, amount, category, discretionaryData, individualName, traceNumber, transactionCode
from addenda05: paymentRelatedInformation
from addenda99: addendaInformation, dateOfDeath, dateOfDeath, originalTrace, returnCode, originalDFI
from addenda98: changeCode, correctedData, originalDFI, originalTrace

IATBatchHeader (that is not in batchHeader): ISODestinationCountryCode, ISOOriginatingCurrencyCode, ISODestinationCurrencyCode
IATEntryDetails: (additional to entryDetails): OFACScreeningIndicator, secondaryOFACScreeningIndicator
addenda10: transactionTypeCode, foreignPaymentAmount
addenda11: name, originatorName, originatorStreetAddress
addenda12: originatorCityStateProvince, originatorCountryPostalCode
addenda13: ODFIName, ODFIIDNumberQualifier, ODFIIdentification, ODFIBranchCountryCode
addenda14: RDFIName, RDFIIDNumberQualifier, RDFIBranchCountryCode (RDFIIdentification also included in entry details)
addenda15: receiverIDNumber, receiverStreetAddress
addenda16: receiverCityStateProvince, receiverCountryPostalCode
addenda17: paymentRelatedInformation
'''

addendaFields = {}

# regular transactions
addendaFields['addenda05'] = ['paymentRelatedInformation']

# IAT
addendaFields['addenda10'] = ['transactionTypeCode', 'foreignPaymentAmount']
addendaFields['addenda11'] = ['name', 'originatorName', 'originatorStreetAddress']
addendaFields['addenda12'] = ['originatorCityStateProvince', 'originatorCountryPostalCode']
addendaFields['addenda13'] = ['ODFIName', 'ODFIIDNumberQualifier', 'ODFIIdentification', 'ODFIBranchCountryCode']
addendaFields['addenda14'] = ['RDFIName', 'RDFIIDNumberQualifier', 'RDFIBranchCountryCode']
addendaFields['addenda15'] = ['receiverIDNumber', 'receiverStreetAddress']
addendaFields['addenda16'] = ['receiverCityStateProvince', 'receiverCountryPostalCode']
addendaFields['addenda17'] = ['paymentRelatedInformation']

# NOC
addendaFields['addenda98'] = ['originalDFI', 'originalTrace', 'changeCode', 'correctedData']

# Returns
addendaFields['addenda99'] = ['originalDFI', 'originalTrace', 'addendaInformation', 'dateOfDeath', 'returnCode']

batchHeaderFields = ['ODFIIdentification', 'companyIdentification', 'companyEntryDescription',\
                      'companyName', 'effectiveEntryDate', 'originatorStatusCode',\
                          'serviceClassCode', 'settlementDate', 'standardEntryClassCode']
entryFields = ['DFIAccountNumber', 'RDFIIdentification', 'amount',\
                'category', 'discretionaryData', 'individualName',\
                      'traceNumber', 'transactionCode', 'OFACScreeningIndicator',\
                          'secondaryOFACScreeningIndicator']
addOnFields = ['traceNumberJoinKey']

all_fields = []
uniq = set()

for lst in (batchHeaderFields, entryFields, [field for fields in addendaFields.values() for field in fields], addOnFields):
    for item in lst:
        if item not in uniq:
            uniq.add(item)
            all_fields.append(item)

# all_fields = ['ODFIIdentification', 'companyIdentification', 'companyEntryDescription',\
#                'companyName', 'effectiveEntryDate', 'originatorStatusCode',\
#                 'serviceClassCode', 'settlementDate', 'standardEntryClassCode',\
#                 'DFIAccountNumber', 'RDFIIdentification', 'amount',\
#                 'category', 'discretionaryData', 'individualName',\
#                 'traceNumber', 'transactionCode', 'OFACScreeningIndicator',\
#                 'secondaryOFACScreeningIndicator', 'paymentRelatedInformation', 'transactionTypeCode',\
#                 'foreignPaymentAmount', 'name', 'originatorName',\
#                 'originatorStreetAddress', 'originatorCityStateProvince', 'originatorCountryPostalCode',\
#                 'ODFIName', 'ODFIIDNumberQualifier', 'ODFIBranchCountryCode',\
#                 'RDFIName', 'RDFIIDNumberQualifier', 'RDFIBranchCountryCode',\
#                 'receiverIDNumber', 'receiverStreetAddress', 'receiverCityStateProvince',\
#                 'receiverCountryPostalCode', 'originalDFI', 'originalTrace',\
#                 'changeCode', 'correctedData', 'addendaInformation',\
#                 'dateOfDeath', 'returnCode', 'traceNumberJoinKey']

def get_data(recordType, batch):
    all_rows = []
    if recordType == 'IATBatches':
        batchHeader = batch["IATBatchHeader"]
        entries = batch["IATEntryDetails"]
    else:
        batchHeader = batch["batchHeader"]
        entries = batch["entryDetails"]

    batchData = {field: str(batchHeader.get(field, "")).strip() for field in batchHeaderFields}

    for entry in entries:

        entryData = {field: str(entry.get(field, "")).strip() for field in entryFields}

        addendaData = {}
        for addendaType, fields in addendaFields.items():
            if addendaType in entry:
                raw_addenda = entry[addendaType]
                # if addenda is list instead of dict, only looking at first item in list for now
                if isinstance(raw_addenda, list):
                    raw_addenda = raw_addenda[0]
                addendaData.update({field: str(raw_addenda.get(field, "")).strip() for field in fields})
        
        # TO-DO: create unique join key to link transactions and returns
        # 'ODFIIdentification', 'companyIdentification', 'companyEntryDescription', 'companyName', 'effectiveEntryDate', 'originatorStatusCode', 'serviceClassCode', 'settlementDate', 'standardEntryClassCode'
        # traceNumberJoinKey = full_data.get('')

        fullData = batchData | entryData | addendaData
        all_rows.append([str(fullData.get(field, "")).strip() for field in all_fields])
    return all_rows
    
all_data = []

for recordType in ['IATBatches', 'NotificationOfChange', 'batches', 'ReturnEntries']:
    if data.get(recordType, None) != None:
        for batch in data.get(recordType, []):
            all_data += get_data(recordType, batch)

# Create the DataFrame and save to file
df = pd.DataFrame(all_data, columns=all_fields)
df.to_csv(out_path, index=False)

print(f"Data has been saved to {out_path}")


    