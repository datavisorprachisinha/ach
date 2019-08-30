package examples

import (
	"fmt"
	"github.com/moov-io/ach"
	"log"
)

func Example_telWriteDebit() {
	fh := mockFileHeader()

	bh := ach.NewBatchHeader()
	bh.ServiceClassCode = ach.DebitsOnly
	bh.CompanyName = "Name on Account"
	bh.CompanyIdentification = fh.ImmediateOrigin
	bh.StandardEntryClassCode = ach.TEL
	bh.CompanyEntryDescription = "Payment"
	bh.EffectiveEntryDate = "190816"
	bh.ODFIIdentification = "121042882"

	entry := ach.NewEntryDetail()
	entry.TransactionCode = ach.CheckingDebit
	entry.SetRDFI("231380104")
	entry.DFIAccountNumber = "12345678"
	entry.Amount = 50000
	entry.SetTraceNumber(bh.ODFIIdentification, 1)
	entry.IndividualName = "Receiver Account Name"

	// build the batch
	batch := ach.NewBatchTEL(bh)
	batch.AddEntry(entry)
	if err := batch.Create(); err != nil {
		log.Fatalf("Unexpected error building batch: %s\n", err)
	}

	// build the file
	file := ach.NewFile()
	file.SetHeader(fh)
	file.AddBatch(batch)
	if err := file.Create(); err != nil {
		log.Fatalf("Unexpected error building file: %s\n", err)
	}

	fmt.Printf("%s", file.Header.String()+"\n")
	fmt.Printf("%s", file.Batches[0].GetHeader().String()+"\n")
	fmt.Printf("%s", file.Batches[0].GetEntries()[0].String()+"\n")
	fmt.Printf("%s", file.Batches[0].GetControl().String()+"\n")
	fmt.Printf("%s", file.Control.String()+"\n")

	// Output:
	// 101 03130001202313801041908161055A094101Federal Reserve Bank   My Bank Name           12345678
	// 5225Name on Account                     231380104 TELPayment         190816   1121042880000001
	// 62723138010412345678         0000050000               Receiver Account Name   0121042880000001
	// 82250000010023138010000000050000000000000000231380104                          121042880000001
	// 9000001000001000000010023138010000000050000000000000000

}
