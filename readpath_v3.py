diseaseterms = ["cancer", "carcinoma", "sarcoma", "melanoma", "adenocarcinoma", "lymphoma", "leukemia", "seminoma", "basal cell carcinoma", "myeloma", "chordoma", "histiocytoma", "mesothlioma", "plasmacytoma", "hypernephroma", "glioma", "glioblastoma", "blastoma", "meningioma", "schwannoma", "carcinoid", "pheochromocytoma", "merkel", "wilms"]
tissueterms = ["breast", "lung", "colon", "skin", "heart", "tongue", "liver", "testicle", "testicular", "hepatocellular", "ocular", "eye", "muscle", "prostate", "ovarian", "stomach", "endometrium", "endometrial", "esophageal", "esophagus", "cervical", "cervix", "pancreatic", "pancreas", "pleural", "ge junction", "rectal", "rectum", "peritoneal", "brain", "bronchial", "kidney", "renal", "gastric", "bowel", "uterus", "uterine", "lobe"]


def parsePath(filename, offset):
    

    with open(filename) as fh:
        fh.seek(offset)
        stepthrough = 0
        PathNumber=""
        SurgDate =""
        SNOmed =""
        ClinHist=""
        Tissue=""
        GrossDesc=""
        MicroDiag=""
        PatientName = ""
        diseasehit=[]
        tissuehit = []
        MRN = ""
        Age = ""


        while stepthrough==0:
            line = fh.readline().rstrip()  #read the first line
            if "Accesssion No:" in line:
                PathNumber = line[15:]
            if "Med Rec No:" in line:
                MRN = line[12:] 
            if "Age:" in line:
                Age = line[5:]       
                #print PathNumber
                stepthrough=2
                break


        while stepthrough == 2:
            line = fh.readline().rstrip()
            if "Surgery Date:" in line:
                SurgDate = line[14:]
                stepthrough = 3

        while stepthrough ==3:
            line = fh.readline().rstrip()
            if "SNOmed Code" in line:   
                SNOmed += line[13:]
                stepthrough =4
                break

        while stepthrough ==4:
            line = fh.readline().rstrip()
            if "SNOmed Code" in line:
                SNOmed += ", "
                SNOmed += line[13:]
            if "PATIENT:" in line: 
                NameLine = line.split(":")[1]
                PatientName = NameLine.split(" PATHOLOGY")[0]
                PatientName = PatientName[1:]
                stepthrough =5
                break

        while stepthrough == 5:
            line = fh.readline().rstrip()
            if "CLINICAL HISTORY:" in line:
                ClinHist += line[18:]
                stepthrough =6
                break

        while stepthrough ==6:
            line = fh.readline().rstrip()
            if "TISSUE SUBMITTED:" in line:
                Tissue = line[18:]
                stepthrough = 7
            if PatientName in line:
                line =""  
            if PathNumber in line:
                line=""        
                

        while "GROSS DESCRIPTION" not in line:
            line = fh.readline().rstrip()
            if "GROSS DESCRIPTION:" in line:
                break
            if PatientName in line:
                line="" 
            if PathNumber in line:
                line=""     
            if len(line) >0:
                Tissue += line

        while "MICROSCOPIC DIAGNOSIS:" not in line:
            line = fh.readline().rstrip()
            if "MICROSCOPIC DIAGNOSIS:" in line:
                MicroDiag += line[23:]
                break
            if PatientName in line:
                line="" 
            if PathNumber in line:
                line=""    
            #if line == "":
                #line = fh.readline().rstrip()
            if len(line) >0:
                GrossDesc += " "
                GrossDesc += line
            if "Pathologist" in line:
                record = PathNumber, SurgDate, SNOmed, ClinHist, Tissue, GrossDesc, MicroDiag, fh.tell(), diseasehit, tissuehit, PatientName, Age, MRN
                return record
        
        while "Pathologist" not in line:
            line = fh.readline().rstrip()
            if "M.D." in line:
                line=""
                break          
                
            if PatientName in line:
                line="" 
            if PathNumber in line:
                line=""             
            if len(line) >0:
                MicroDiag += " "
                MicroDiag += line
                  
            stringtosearch = ClinHist + Tissue + GrossDesc + MicroDiag
            stringtosearch = stringtosearch.lower() # to avoid case mismatches eg Prostate v prostate
    
            #print v
            
            for d in diseaseterms:
                
                if d in stringtosearch:
                    if d not in diseasehit:
                        diseasehit.append(d)
                if len(diseasehit) >0:
                    for t in tissueterms:
                        if t in stringtosearch:
                            if t not in tissuehit:
                                tissuehit.append(t)
                
            
        record = PathNumber, SurgDate, SNOmed, ClinHist, Tissue, GrossDesc, MicroDiag, fh.tell(), diseasehit, tissuehit, PatientName, Age, MRN
    return record

lastreadoffset = 0

increment = 0
PathDict = {}

print "Loading all Pathology Reports and scanning for cancer-related terms..."
print

while increment < 152000:
    record = parsePath("path1996_accessible.txt", lastreadoffset) # hard code the file name in here or rewrite to interactively ask for filename
    lastreadoffset = record[7]
    


    PathDict[record[0]] = record
    increment +=1
    if record [0] == "S96-05277": #stopping at last record to avoid EOF hanging. Need to hardcode this each year
        increment = 10000000000

print "Number of total records found:" , len(PathDict)
print


f = open("readparseoutput.txt", 'w')
headers = "Pathology No." + '\t' + "Patient Name"+ '\t' +"Patient Age"+ '\t' +"MRN"+ '\t' +"Surgery Date" + '\t' + "SnoMed Terms"+ '\t' + "Clinical History" + '\t' + "Tissue Submitted" + '\t' +"Gross Description" + '\t' +"Microscopic Diagnosis" + '\t' +"Disease terms" + '\t' +"Tissue terms" + '\n'
f.write (headers)
for key, value in PathDict.iteritems():
    outputline = value[0] + '\t' + value[10] + '\t' +value[11]+ '\t' +value[12]+ '\t' + value[1] + '\t' + value [2] + '\t' + value [3]+ '\t' + value [4]+ '\t' + value [5] + '\t' + value [6]+ '\t' + str(value [8])+ '\t' + str(value [9]) +'\n'
    f.write(outputline)
f.close()

print "A Tab-Delimited Table of all records can be found in readparseoutput.txt"
print

f = open("readparseoutput_cancer only.txt", 'w')
headers = "Pathology No." + '\t' + "Patient Name"+ '\t' +"Patient Age"+ '\t' +"MRN"+ '\t' +"Surgery Date" + '\t' + "SnoMed Terms"+ '\t' + "Clinical History" + '\t' + "Tissue Submitted" + '\t' +"Gross Description" + '\t' +"Microscopic Diagnosis" + '\t' +"Disease terms" + '\t' +"Tissue terms" + '\n'
f.write (headers)
for key, value in PathDict.iteritems():
    if len(value[8]) >0 and "basal cell carcinoma" not in value[8]:
        outputline = value[0] + '\t' + value[10] + '\t' +value[11]+ '\t' +value[12]+ '\t' + value[1] + '\t' + value [2] + '\t' + value [3]+ '\t' + value [4]+ '\t' + value [5] + '\t' + value [6]+ '\t' + str(value [8])+ '\t' + str(value [9]) +'\n'
        f.write(outputline)
f.close()

print"Eliminating non-cancer and basal cell carcinoma cases..."
print
print "A Tab-Delimited Table of cancer cases can be found in readparseoutput.txt"
print
print "Writing individual cancer pathology reports to C:\\readpathoutput"
print

import os

filenumbers = 0
for key, value in PathDict.iteritems():
    if len(value[8]) >0 and "basal cell carcinoma" not in value[8]:
        path = "c:\\readpathoutput"
        filename = value[0]+".txt"
        pathfilename = os.path.join(path, filename)
        #print "pathfilename:", pathfilename
       
        f = open(pathfilename, "w")
        report = "Biobank Pathology Report Summary\n\n" + "PATHOLOGY NUMBER: " + value[0] + "\n\nPatient Name: " +value[10]+ "\n\nPatient Age: "+value[11]+ "\n\nPatient MRN:"+ value[12]+ "\n\nSURGERY DATE: " + value[1] + "\n\nSNOmed Terms: " + value[2] + "\n\nCLINICAL HISTORY: \n\n" + value[3] +"\n\nTISSUE SUBMITTED:\n\n" + value [4] + "\n\nGROSS DESCRIPTION:\n\n" + value[5] +"\n\nMICROSCOPIC DIAGNOSIS:\n\n" + value[6] + "\n\n\nBiobank Note: The following disease and tissue terms were automatically extracted from this report, however the report should be read in its entirety to verify the tissue and diagnosis:\n" + str(value[8]) + str(value[9])
        f.write(report)
        f.close
        filenumbers +=1

for key, value in PathDict.iteritems():
    if len(value[8]) >0 and "basal cell carcinoma" not in value[8]:
        path = "c:\\readpathoutput"
        filename = "Deidentified_"+value[0]+".txt"
        pathfilename = os.path.join(path, filename)
        #print "pathfilename:", pathfilename
       
        f = open(pathfilename, "w")
        report = "Biobank Pathology Report Summary\n\n" + "PATHOLOGY NUMBER: REDACTED" + "\n\nSURGERY DATE: " + value[1] + "\n\nSNOmed Terms: " + value[2] + "\n\nCLINICAL HISTORY: \n\n" + value[3] +"\n\nTISSUE SUBMITTED:\n\n" + value [4] + "\n\nGROSS DESCRIPTION:\n\n" + value[5] +"\n\nMICROSCOPIC DIAGNOSIS:\n\n" + value[6] + "\n\n\nBiobank Note: The following disease and tissue terms were automatically extracted from this report, however the report should be read in its entirety to verify the tissue and diagnosis:\n" + str(value[8]) + str(value[9])
        f.write(report)
        f.close
        


print "A total of", filenumbers, "cancer cases were found and are ready for review."


