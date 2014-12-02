'''
kGt3.py
Bryan Lewandowski

Take the payment_graph_physician_company.csv data, strip out all entries
which either give to or recieve-from <= 3 payments/doctors.  In other words,
removes all doctors with <=3 payments, removes all company/communities
with <= 3 members.
'''

import os
import math
from subprocess import call


'''
Plot a CCDF in gnuplot.
Inputs: filename, a tab sep file for gnuplot to injest (columns 1,2)
   title, the title of the plot.
Output: (a gnuplot .png file is created)
'''
def plotCCDF(filename, title):
   gnuplotarg = '-e "filenameIn=\''+filename+'\'; titleIn=\''+title+'\'"'
   os.system( "gnuplot "+gnuplotarg+" plotCCDF.plt" )


'''
Plot a log-log plot, provided x, y axis titles and graph title.
'''
def plotLogLog(filename, title, xtitle="x", ytitle="y"):
   gnuplotarg = '-e "filenameIn=\''+filename+'\'; titleIn=\''+title+'\'; xIn=\''+xtitle+'\'; yIn=\''+ytitle+'\'"'
   os.system( "gnuplot "+gnuplotarg+" plotLogLog.plt" )


'''
Write a line in a tab file (like gnuplot takes as input).
'''
def writeTab(fout, x, y, z=None):
   fout.write(str(x))
   fout.write('\t')
   fout.write(str(y))
   if z is not None:
      fout.write('\t')
      fout.write(str(z))   
   fout.write('\n')


'''
Write out a histogram file in gnuplot-friendly tab-sep format.
Inputs: d, a dictionary of {int,float} -> {int,float}, which will be
   interpreted in the plot as x -> y
   filename, a filename to use in the output file, ".tab" will be appended.
   comment, an optional comment to put in the header of the file.
Outputs: a file "filename.tab", where filename is the input variable.
'''
def writeHistogramFile(filename, d, comment=""):
   with open(filename+".tab", "w") as fout:
      if len(comment) > 0:
         fout.write('# '+comment+'\n')
      for k in sorted(d):
         writeTab(fout, k, d[k])
      

'''
Produce a payment count histogram.
Input: a dict: int -> [float(actually any)], which is a doctor to a list of
      payments.
Returns: a dict: int -> int, which is a integer number of payments to the
      number of doctors who received that many payments.
'''
def genPaymentCountHistogram(d):
   hist = dict()
   for k in d:
      numPayments = len(d[k])
      if numPayments not in hist:
         hist[numPayments] = 0
      hist[numPayments] += 1
   return hist


'''
Return a dictionary of the total payments made to/from a doctor/company.
Input: a dictionary of int(doctor or companyID) -> [float(payments in $)]
Returns a dict of int(same doctor or companyID as input) -> float (the
   sum of payments to/from that doctor/company.
'''
def sumPayments(d):
   p = dict()
   for k in d:
      p[k] = sum(d[k])
   return p


'''
Payments to number of doctors in that bin histogram.
Input: d:  a dict int(doctor/companyID) -> float(total payments a doctor
   or company recvd/made)
   binsize: the size of a bin (in dollars, must be > 0).  Bins in the
      output are upper bounds (so bin 0 represents the number
      of doctors/companies involved in total payments between
      0 <= x < binsize
Output: a binned dict float($) -> int(count), which is the lower bound
   of a bin (size per input), and the number of doctors/companies who
   fall in that bin.
'''
def paymentAmountHistogram(d, binsize):
   assert(binsize > 0)
   out = dict() # float -> int
   for k in d:
      binNum = int( d[k] / binsize )
      if binNum*binsize not in out:
         out[binNum*binsize] = 0
      out[binNum*binsize] += 1
   return out


'''
Given an input histogram dict, compute the CCDF (the fraction of the
dataset with value >= x.
Input: hist, a dict {int,float} -> int, a histogram, where the first
   value (key) is the "y" and the second is the count of datapoints.
'''
def ccdfFromHistogram(hist):
   datasize = sum( hist.values() )
   out = dict() # {int,float whatever the key is} -> float(1-0)
   obsdata = 0  # accumulator for observed data (discards in CCDF)
   for k in sorted(hist):
      out[k] = (datasize - obsdata) / float(datasize)
      assert(out[k] >= 0. and out[k] <= 1.)
      obsdata += hist[k]
   return out


'''
Print secondary statistics.
Inputs:
   cosToDocs, dict() of company -> set of doctors paid
   docsToCos, dict() of doctor -> set of companies recvd from
Outputs: (.tab files and gnuplot-generated .png images)
'''
def printSecondaries(cosToDocs, docsToCos):
   # Generate a histogram
   # Note: all the input data has been coalesced into one company->doc
   #       link, so this is the same as docs_payment_count_hist.tab
   # (number of companies x) (#docs paid by exactly x companies)
   numCoToNumDocs = dict()
   for k in docsToCos:
      cosToThisDoc = len(docsToCos[k])
      if cosToThisDoc not in numCoToNumDocs:
         numCoToNumDocs[cosToThisDoc] = 0
      numCoToNumDocs[cosToThisDoc] += 1

   writeHistogramFile("secondary_numcos_docsPaidByNumCos_hist", numCoToNumDocs, "NumberOfCompaniesX   NumberOfDocsPaidByExactlyXCompanies")

   # Average degree of a doctor (how many companies pay the doc).
   docDegSum = 0.
   for d in docsToCos:
      docDegSum += len( docsToCos[d] )
   docDegSum /= len(docsToCos)
   print "Average degree of a doctor (# cos pay the doc): %f" %(docDegSum)

   # Average degree of a company (how many doctors they pay).
   coDegSum = 0.
   for d in cosToDocs:
      coDegSum += len( cosToDocs[d] )
   coDegSum /= len(cosToDocs)
   print "Average degree of a company (# docs they pay): %f" %(coDegSum)
  


'''
Parse the input file, using an ignore/removal set, and process the file
into data structures.  Optionally, writes the filtered data out to a
file in the same input format (eg: filter the original).
Returns:
   cos = dict() # company -> list of payments made
   docs = dict() # doc/providerId -> list of payments recvd
   cosToDocs = dict() # company -> set of doctors paid
   docsToCos = dict() # doctor -> set of companies recvd from
   badLines = [] # integer of bad line numbers in data
   rawTotalPayments = 0.
'''
def fileToStructures(filename, skipCos=None, skipDocs=None, fileOutPrefix=""):
   outFile = None
   # A few variables used for sanity checks
   NUM_DOCS = 0
   NUM_COS = 0
   if fileOutPrefix != "":
      outFile = open(fileOutPrefix + filename, "w")

   i = 0
   printBadLines = False
   badLines = [] # integer of bad line numbers in data
   rawTotalPayments = 0.
   cos = dict() # company -> list of payments made
   docs = dict() # doc/providerId -> list of payments recvd
   cosToDocs = dict() # company -> set of doctors paid
   docsToCos = dict() # doctor -> set of companies recvd from
   
   with open(filename) as fin:
      for line in fin:
         s = line.split()
         i += 1
         if i == 1:
            if outFile is not None:
               outFile.write(line)
            continue # header line
         if(len(s)!=3):
            if(printBadLines):
               print "==== Problem on line %d" %(i)
               print line
               print s
               print str(len(s))
            badLines.append(i)
            continue
         doc = int(s[0])
         co = int(s[1])
         amount = float(s[2])

         # Filters
         if skipCos is not None and co in skipCos:
            #print "skipping co ",str(co)
            continue
         if skipDocs is not None and doc in skipDocs:
            #print "skipping doc ",str(doc)
            continue

         if doc not in docs:
            docs[doc] = []
            docsToCos[doc] = set()
            NUM_DOCS += 1
         if co not in cos:
            cos[co] = []
            cosToDocs[co] = set()
            NUM_COS += 1
         docs[doc].append(amount)
         cos[co].append(amount)
         docsToCos[doc].add(co)
         cosToDocs[co].add(doc)
         rawTotalPayments += amount
         #print doc, " ", co, " ", amount
         if outFile is not None:
            writeTab(outFile, doc, co, amount)

   if outFile is not None:
      outFile.close()

   # debug only
   if skipCos is None and skipDocs is None:
      print "Did debug check"
      assert(NUM_COS == len(cos))
      assert(NUM_DOCS == len(docs))

   return cos, docs, cosToDocs, docsToCos, badLines, rawTotalPayments



def k3Trim(filename):
   # Core structures
   #cos = dict() # company -> list of payments made
   #docs = dict() # doc/providerId -> list of payments recvd

   # Secondary structures (added later)
   #cosToDocs = dict() # company -> set of doctors paid
   #docsToCos = dict() # doctor -> set of companies recvd from

   #rawTotalPayments = 0.
   # First pass, no filters.
   cosA, docsA, cosToDocsA, docsToCosA, badlinesA, rawTotalPaymentsA = fileToStructures(filename)

   MIN_DOC_K = 3
   MIN_CO_K = 3
   # Filter data
   removeDocs = set() # doctor Ids to remove (k(doc) < MIN_DOC_K)
   removeCos = set() # company Ids to remove (k(co) < MIN_CO_K)
   for d in docsToCosA:
      if len(docsToCosA[d]) < MIN_DOC_K:
         removeDocs.add(d)
   for c in cosToDocsA:
      if len(cosToDocsA[c]) < MIN_CO_K:
         removeCos.add(c)

   print "======= k removals ========"
   print "Removed docs with < " + str(MIN_DOC_K) + " payments recvd"
   print "Removed companies with < " + str(MIN_CO_K) + " payments made"
   print "docs removed: ", len(removeDocs)
   print "cos removed: ", len(removeCos)
   
   # Second pass, filter and output a new "input" file.
#def fileToStructures(filename, skipCos=None, skipDocs=None, fileOutPrefix=""):
   
   filePrefix = "minK_doc_"+str(MIN_DOC_K)+"_co_"+str(MIN_CO_K)+"_"
   cos, docs, cosToDocs, docsToCos, badlines, rawTotalPayments = fileToStructures(filename, removeCos, removeDocs, filePrefix)
   
   
   
   
   
   
   
   
   
   
   assert(False)

   print "==== Results ===="
   print "Bad lines in file (lines excluded): %d" %(len(badLines))
   print "Num payments (good lines): %d" %(i - len(badLines))
   print "Num providers/docs: %d" %(len(docs))
   print "Num companies/payers: %d" %(len(cos))
   maxPayout = max([v for sub in cos.values() for v in sub])
   print "Largest payout %f" %(maxPayout)
   maxPayin = max([v for sub in docs.values() for v in sub])
   print "Largest payin %f" %(maxPayin)

   coTotalPayments = 0.
   for c in cos:
      for p in cos[c]:
         coTotalPayments += p
   totalPayments = sum([v for sub in docs.values() for v in sub])
   print "Total of all payments %f" %(totalPayments)
   print "Total of all paymentsC %f" %(coTotalPayments)
   print "Total of all paymentsRaw %f" %(rawTotalPayments)

   cosPaymentCountHist = genPaymentCountHistogram(cos)
   assert(NUM_COS == sum( cosPaymentCountHist.values() ))

   docsPaymentCountHist = genPaymentCountHistogram(docs)
   assert(NUM_DOCS == sum( docsPaymentCountHist.values() ))

   #print "cos: Num payments, num companies making that many payments"
   #for k in sorted(cosPaymentCountHist):
   #   print "%d %d" %(k, cosPaymentCountHist[k])

   #print "docs: Num payments, num doctors recieving that many payments"
   #for k in sorted(docsPaymentCountHist):
   #   print "%d %d" %(k, docsPaymentCountHist[k])

   cosSumPayments = sumPayments(cos)
   assert(NUM_COS == len(cosSumPayments))
   docsSumPayments = sumPayments(docs)
   assert(NUM_DOCS == len(docsSumPayments))

   binsize = 10.
   cosPaymentDollarsHist = paymentAmountHistogram(cosSumPayments, binsize)
   assert(NUM_COS == sum( cosPaymentDollarsHist.values() ))
   docsPaymentDollarsHist = paymentAmountHistogram(docsSumPayments, binsize)
   assert(NUM_DOCS == sum( docsPaymentDollarsHist.values() ))

   #print "cos: Payment histogram: payment->+%f, num cos making that much in total payments" %(binsize)
   #for k in sorted(cosPaymentDollarsHist):
   #   print "%f %d" %(k, cosPaymentDollarsHist[k])

   #print "docs: Payment histogram: payment->+%f, num docs taking that much in total payments" %(binsize)
   #for k in sorted(docsPaymentDollarsHist):
   #   print "%f %d" %(k, docsPaymentDollarsHist[k])

   # Write out histogram files for gnuplot.
   writeHistogramFile("cos_payment_count_hist", cosPaymentCountHist, "NumberOfPayments   NumberOfCompaniesMakingThatManyPayments")
   writeHistogramFile("docs_payment_count_hist", docsPaymentCountHist, "NumberOfPayments   NumberOfDoctorsReceivingThatManyPayments")
   writeHistogramFile("cos_payment_dollars_hist", cosPaymentDollarsHist, "TotalOfPaymentsDollars   NumCompaniesMakingThatMuchInTotalPayments")
   writeHistogramFile("docs_payment_dollars_hist", docsPaymentDollarsHist, "TotalOfPaymentsDollars   NumDoctorsTakingThatMuchInTotalPayments")

   # Plot histograms for gnuplot.
   plotLogLog("docs_payment_count_hist.tab", "Doctor(node) to community degree distribution histogram", "Degree", "Number of Doctors")


   # Create CCDF distributions (counts at or above the level).
   cosPaymentCountCCDF = ccdfFromHistogram(cosPaymentCountHist)
   docsPaymentCountCCDF = ccdfFromHistogram(docsPaymentCountHist)
   cosPaymentDollarsCCDF = ccdfFromHistogram(cosPaymentDollarsHist)
   docsPaymentDollarsCCDF = ccdfFromHistogram(docsPaymentDollarsHist)

   # Write out CCDF distributions for gnuplot.
   writeHistogramFile("cos_payment_count_ccdf", cosPaymentCountCCDF, "NumberOfPayments   RatioOfCompaniesMaking>=ThatManyPayments")
   writeHistogramFile("docs_payment_count_ccdf", docsPaymentCountCCDF, "NumberOfPayments   RatioOfDoctorsReceiving>=ThatManyPayments")
   writeHistogramFile("cos_payment_dollars_ccdf", cosPaymentDollarsCCDF, "TotalOfPaymentsDollars   RatioCompaniesMaking>=ThatMuchInTotalPayments")
   writeHistogramFile("docs_payment_dollars_ccdf", docsPaymentDollarsCCDF, "TotalOfPaymentsDollars   RatioDoctorsTaking>=ThatMuchInTotalPayments")

   # Plot file for gnuplot
   plotCCDF("cos_payment_count_ccdf.tab", "CCDF, x is number of payments, y is % of companies making >= that many payments")
   plotCCDF("docs_payment_count_ccdf.tab", "CCDF, x is number of payments, y is % of doctors taking >= that many payments")
   plotCCDF("cos_payment_dollars_ccdf.tab", "CCDF, x is total value $ of payments, y is % of companies making >= that total amount ($) of payments")
   plotCCDF("docs_payment_dollars_ccdf.tab", "CCDF, x is total value $ of payments, y is % of doctors taking >= that total amount ($) of payments")

   # Secondary stastics
   printSecondaries(cosToDocs, docsToCos)


if __name__ == "__main__":
   "Generating statistics"
   filename = "payment_graph_physician_company.csv"
   k3Trim(filename)
