diseaseterms = ["cancer", "carcinoma", "sarcoma", "melanoma", "adenocarcinoma", "lymphoma", "leukemia", "seminoma", "basal cell carcinoma", "myeloma", "chordoma", "histiocytoma", "mesothlioma", "plasmacytoma", "hypernephroma", "glioma", "glioblastoma", "blastoma", "meningioma", "schwannoma", "carcinoid", "pheochromocytoma", "merkel", "wilms"]
tissueterms = ["breast", "lung", "colon", "skin", "heart", "tongue", "liver", "testicle", "testicular", "hepatocellular", "ocular", "eye", "muscle", "prostate", "ovarian", "stomach", "endometrium", "endometrial", "esophageal", "esophagus", "cervical", "cervix", "pancreatic", "pancreas", "pleural", "ge junction", "rectal", "rectum", "peritoneal", "brain", "bronchial", "kidney", "renal", "gastric", "bowel", "uterus", "uterine", "lobe"]

def parsePath(filename, offset):
    
    import os
    
    with open(filename) as fh:
        fh.seek(offset)
        stepthrough = 0
        diseasehit=[]
        tissuehit = []
        RightmostDashPos = 0
        LineLength = 0
        PathNoIndex = 0
        StartingNewRecord = 0

        while True:
            line = fh.readline().rstrip()  #read the first line
            line = line.replace("\t", " ") #removes any internal tabs, replacing with a space
            line = line.replace("CLINICAL HISTORY", "\n\nCLINICAL HISTORY") #add carriage return before section headings for better report format
            line = line.replace("GROSS DESCRIPTION", "\n\nGROSS DESCRIPTION")
            line = line.replace("MICROSCOPIC DIAGNOSIS", "\n\nMICROSCOPIC DIAGNOSIS")
            line = line.replace("MICROSCOPIC", "\n\nMICROSCOPIC")
            line = line.replace("TISSUE SUBMITTED", "\n\nTISSUE SUBMITTED")
            line = line.replace("54601", "54601\n\n")
            
            if 'PATHOLOGY' in line and "NO." in line and ("PATIENT" in line or "AGE" in line) and StartingNewRecord == 0:  #Defining feature of GHS Pathology report header
                line = line.replace("\xb7", "")
                line = line.replace("PATIENT", " PATIENT") #cleanup for accurate PathID parsing
                line = line.replace("CLINIC", " CLINIC")
                line = line.replace("SURGEON", " SURGEON")
                line = line.replace("'", " ")
                line = line.replace(" -", "-")
                line = line + " "

                StartingNewRecord = 1
                PathNoIndex = line.index('PATH') #finds the location of the Pathology No. flag to allow splitting line
               
                SubstringWithPath = line[PathNoIndex:] #isolate portion of line after Pathology No. to exclude hyphenated patient names
                
                ListWithPath = SubstringWithPath.split()      #splits the string into a list, using the spaces to divide

                PathID = list(filter(lambda element: '-' in element, ListWithPath)) #returns list element containing the -, typically the Path No.
                                
                #Next block of code is repairs several common errors in PathID parsing due to OCR-related issues
                del PathID[1:]                      #removes all items after the first one in list e.g. hyphenated names of surgeons
                PathID = str(PathID)                #converts list element to string
                
                PathID = PathID.replace(" ", "")    #removes any spaces from PathID
                PathID = PathID.replace(".", "")    #removes any dots from PathID
                PathID = PathID.replace("~", "")    #removes and tildes from PathID
                PathID = PathID.replace(")", "")
                if len(str(PathID)) ==2:
                    PathID = "S" + Year + "XXXXX"  
                     
                if PathID[0] == "-":
                    PathID = "S"+ Year + PathID
                   
                if PathID[1] == "-":
                    PathID = "S"+ Year + PathID[1:] 
                    
                if PathID[2] == "-":
                    PathID = "S"+ Year + PathID[2:]   
                    
                if PathID[3] == "-":
                    PathID = "['S"+ Year + PathID[3:]   
                    
                if PathID[4] == "-":
                    PathID = "['S"+ Year + PathID[4:]   
                    
                PathID = "S" + PathID[3:-2]         #replaces first character in PathID with S to repair OCR errors which sometimes represent S as 5 or 8
                
                PathID = PathID[:4]+str(PathID[4:].zfill(5))   #add leading zeros for five digits after dash
                if PathID[:3] != str("S"+Year):
                    PathID = "S"+Year+PathID[3:]
                if PathID.count("-") > 1:                       #for cases of generation of compound IDs - adds a series of X's to flag issue
                    PathID = "XXXXX" + PathID    
                if PathID[5:].isdigit() == False:                #to flag PathIDs with numbers that got scanned or recognized as letters
                    PathID = "XXXXX" + PathID    
               
                RecordText = line
               
            elif 'PATHOLOGY' not in line and "NO." not in line and ("PATIENT" not in line or "AGE" not in line) and StartingNewRecord == 1:
                RecordText += line              #Add new lines to the text of the record until a new header is encountered
                LastNonHeaderOffset = fh.tell() #updates each time a line that is not a header is read so that this can be passed as new offset once header is found
                LastNonHeaderOffset = LastNonHeaderOffset - 50

                if fh.tell() == os.stat(filename).st_size: #Stops gathering text from the final record when it gets to last line of the file
                    increment = 100000000000               #sets the increment to really high number to terminate the external calls to ParsePath
                    return PathID, RecordText, LastNonHeaderOffset

            elif 'PATHOLOGY' in line and "NO." and ("PATIENT" in line or "AGE" in line) and StartingNewRecord == 1:   #Found next header while reading last record
                
                StartingNewRecord = 0                                                          #Reset counter, don't add line

                return PathID, RecordText, LastNonHeaderOffset

Year =raw_input("What is the last two digits of the year (e.g. for 1991 enter 91)?")
print
filename = raw_input("Enter filename of text file in this directory: ")
print
LastReportInFile = raw_input("Enter Pathology ID of the last report in file (e.g. S91-15851): ")
lastreadoffset = 0

import time                  #to calculate run time
start_time = time.time()

increment = 0
PathDict = {}

print
print "Loading all Pathology Reports and scanning for cancer-related terms..."
print "This may take a couple of minutes..."
print

while increment < 152000:                                       #sets up a very high value to ensure looping through all records
    record = parsePath(filename, lastreadoffset) # calls parsepath function on the file, letting it know the correct point from which to start reading
    
    lastreadoffset = record[2]
        
    stringtosearch = record[1]
    stringtosearch = stringtosearch.lower() # to avoid case mismatches eg Prostate v prostate
          
    diseasehit = []
    tissuehit = []        
    for d in diseaseterms:                  # search record for terms matching diseases
                
        if d in stringtosearch:
                if d not in diseasehit:
                    diseasehit.append(d)
                if len(diseasehit) >0:                  #where a disease term was identified, retrieve tissue terms from record
                    for t in tissueterms:           
                        if t in stringtosearch:
                            if t not in tissuehit:
                                tissuehit.append(t)

    diseasehit = str(diseasehit)
    tissuehit = str(tissuehit)

    RecordWithHits = (record[1], diseasehit, tissuehit)


    if record[0] in PathDict.keys():                #checks if a case with this PathID exists, if it does adds new case with a modified PathID to avoid displacing previous case from PathDict
        PathDict[str(record[0])+"_"+str(increment)] = RecordWithHits 
    elif record[0] not in PathDict.keys():          #If PathID not already in dictionary, adds it and the rest of the case details
        PathDict[record[0]] = RecordWithHits

 

    increment +=1
    if record [0] == LastReportInFile: #stopping at last record to avoid EOF hanging. Need to hardcode this each year
        increment = 10000000000

print "Number of total records found:" , len(PathDict)
print

# Write out one tab-delimited text file containg one each line PathID, text of report, disease terms and tissue terms

f = open("readparsescanoutput.txt", 'w')
headers = "Pathology No." + '\t' + "Report" +'\t'+ "Disease Term" +'\t'+ "Tissue Term" +'\n' 
f.write (headers)
for key, value in PathDict.iteritems():
    diseasehit = str(value[1])
    tissuehit = str(value[2])
    outputline = key + '\t' + str(value[0]).replace('\n'," ") +'\t'+ diseasehit +'\t'+ tissuehit +'\n' #need to get rid of added newlines from [0] for tab-delim text
    f.write(outputline)
f.close()

print "A Tab-Delimited Table of all records can be found in readparsescanoutput.txt"
print

# Write out one tab-delimited text file containing only the reports flagged as possible cancer cases

f = open("readparsescanoutput_cancer only.txt", 'w')
headers = "Pathology No." + '\t' + "Report" +'\t'+ "Disease Term" +'\t'+ "Tissue Term" +'\n' 
f.write (headers)
for key, value in PathDict.iteritems():
    if len (str(value[1])) > 3 and "basal cell carcinoma" not in str(value[1]):
        outputline = key + '\t' + str(value[0]).replace('\n'," ") +'\t'+ str(value[1]) +'\t'+ str(value[2]) +'\n'
        f.write(outputline)
f.close()

print"Eliminating non-cancer and basal cell carcinoma cases..."
print
print "A Tab-Delimited Table of cancer cases can be found in readparsescanoutput_cancer_Only.txt"
print
print "Writing individual cancer pathology reports to C:\\readpathscanoutput"
print

import os

filenumbers = 0
for key, value in PathDict.iteritems():
    if len(value[1]) >3 and "basal cell carcinoma" not in value[1]:
        path = "c:\\readpathscanoutput"
        filename = key+".txt"                         #each file has name formatted as PathID.txt
        pathfilename = os.path.join(path, filename)
               
        f = open(pathfilename, "w")
       
        report = "Biobank Pathology Report Summary\n\n" + "PATHOLOGY NUMBER: " + key + "[Note: Path No. electronically generated. Confirm by checking text below and original scanned report]" + "\n\nScanned Report:\n " +value[0]+  "\n\n\nBiobank Note: The following disease and tissue terms were automatically extracted from this report, however the report should be read in its entirety to verify the tissue and diagnosis:\n" + str(value[1]) + str(value[2])
        f.write(report)
        f.close
        filenumbers +=1

print "A total of", filenumbers, "cancer cases were found and are ready for review."
print
print "Total analysis time: " +str(time.time()-start_time) + " seconds."


