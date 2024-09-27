// Licensed to The Moov Authors under one or more contributor
// license agreements. See the NOTICE file distributed with
// this work for additional information regarding copyright
// ownership. The Moov Authors licenses this file to you under
// the Apache License, Version 2.0 (the "License"); you may
// not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing,
// software distributed under the License is distributed on an
// "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
// KIND, either express or implied.  See the License for the
// specific language governing permissions and limitations
// under the License.

package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"

	"github.com/moov-io/ach"
)

var (
	inPath  = flag.String("inPath", "", "File Path read from")
	outPath = flag.String("outPath", "", "File Path write out to")
)

func main() {
	flag.Parse()

	inPath := *inPath

	// open a file for reading. Any io.Reader Can be used
	f, err := os.Open(inPath)

	if err != nil {
		log.Printf("ERROR: Can not open file: %s: \n", err)
		os.Exit(1)
	}

	achFile, err := ach.NewReader(f).Read()
	if err != nil {
		fmt.Printf("Issue reading file: %+v \n", err)
	}

	// If you trust the file but it's formating is off building will probably resolve the malformed file.
	if err := achFile.Create(); err != nil {
		fmt.Printf("Could not create file with read properties: %v", err)
	}

	// ensure we have a validated file structure
	if err := achFile.Validate(); err != nil {
		fmt.Printf("Could not validate entire read file: %v", err)
	}

	// Create or open the file for writing
	outPath := *outPath
	outFile, err := os.Create(outPath)
	if err != nil {
		log.Fatalf("failed to create file: %v", err)
	}
	defer outFile.Close() // Ensure the file is closed when we're done

	// Output file contents
	if err := json.NewEncoder(outFile).Encode(achFile); err != nil {
		fmt.Printf("ERROR: problem writing ACH File to stdout: %v\n", err)
		os.Exit(1)
	}
}
