# Pathology-Report-Parser
Scripts to parse files containing pathology reports into individual pathology reports, search each for a list of terms and output summary of all reports and individual files for reports matching key terms.

Two python scripts included. One script (readpath_v3) works for electronically generated reports e.g. PDF reports issued by hospital from a formal electronic system where the format does not vary. The second script (readscanpath_v3) works on PDFs generated from scanned paper pathology reports from which the text has been recognized by OCR using a program such as Adobe Acrobat. Because of difficulties inherent in the latter approach (misrecognition of characters (e.g. i v I v l etc) this script makes extensive efforts to read and correct the scanned Pathology ID which acts as the unique identier for each individual report.

Depending on the source of reports to be scanned, the code in each script which is used to recognize the header signifying the start of a new report needs to be modified.

Both scripts require the creation of a directory on C:\ to receive the individual text files corresponding to pathology reports meeting the criteria.

New criteria can be added to the diseaseterms list at the start of each script.
