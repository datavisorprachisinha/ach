import json 
import pandas as pd

file_path = '/Users/prachisinha/Desktop/nasa/raw_nacha_files/aws-uswest2-prod-eng-jumpserver-3/ACHAJ11255077833PDIN20240910150403404.json'

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
from addenda99: addendaInformation, dateOfDeath, dateOfDeath, originalTrace, returnCode
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

batchHeaderFields = ['ODFIIdentification', 'companyIdentification', 'companyEntryDescription', 'companyName', 'effectiveEntryDate', 'originatorStatusCode', 'serviceClassCode', 'settlementDate', 'standardEntryClassCode']
entryFields = ['DFIAccountNumber', 'RDFIIdentification', 'amount', 'category', 'discretionaryData', 'individualName', 'traceNumber', 'transactionCode', 'OFACScreeningIndicator', 'secondaryOFACScreeningIndicator']
addOnFields = ['traceNumberJoinKey']

all_fields = batchHeaderFields + entryFields + [field for fields in addendaFields.values for field in fields] + addOnFields

def get_data(recordType, batchHeader, batchData):
    all_rows = []
    if record_type == 'IATBatches':
        batchHeader = batch["IATBatchHeader"]
        entries = batch["IATEntryDetails"]
    else:
        batchHeader = batch["batchHeader"]
        entries = batch["entryDetails"]

    batchData = [str(batchHeader.get(field, "")).strip() for field in batchHeaderFields]

    for entry in entries:
        full_data = {}
        entryData = [str(entry.get(field, "")).strip() for field in entryFields]

        for addenda, fields in addendaFields.itmes():
            if addenda in entry:
                addendaData = entry[addenda]
                # if addenda is list instead of dict, only looking at first item in list for now
                if isinstance(addendaData, list):
                    addendaData = addendaData[0]
                for field in fields:
                    full_data[field] = str(addendaData.get(field, "")).strip()
        
        # not sure what IAT return looks like since the batch header is different
        'ODFIIdentification', 'companyIdentification', 'companyEntryDescription', 'companyName', 'effectiveEntryDate', 'originatorStatusCode', 'serviceClassCode', 'settlementDate', 'standardEntryClassCode'
        traceNumberJoinKey = full_data.get('')

        full_data = batchData + entryData + addenda05Data + addenda99Data + addenda98Data + addendaCommonData
        all_rows.append(full_data)
    return all_rows
    
all_data = []

for record_type in ['NotificationOfChange', 'batches', 'ReturnEntries']:
    # print(data[record_type])
    if data[record_type] != None:
        for batch in data.get(record_type, []):
            all_data += get_data(batch)

# Create the DataFrame
df = pd.DataFrame(all_data, columns=all_fields)

# save the DataFrame to a CSV file
out_path = '/Users/prachisinha/Desktop/nasa/raw_nacha_files/aws-uswest2-prod-eng-jumpserver-3/ACHAJ11255077833PDIN20240910150403404_parsed.csv'
df.to_csv(out_path, index=False)

print(f"Data has been saved to {out_path}")


    