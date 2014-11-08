'''

Bryan Lewandowski

Generate basic stats about the payment_graph_physician_company.csv
data.
'''

import math





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


def printStats(filename):
   # A few variables used for sanity checks
   NUM_DOCS = 0
   NUM_COS = 0
   printBadLines = False
   
   cos = dict() # company -> list of payments made
   docs = dict() # doc/providerId -> list of payments recvd

   i = 0
   badLines = [] # integer of bad line numbers in data
   with open(filename) as fin:
      for line in fin:
         s = line.split()
         i += 1
         if i == 1:
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
         if doc not in docs:
            docs[doc] = []
            NUM_DOCS += 1
         if co not in cos:
            cos[co] = []
            NUM_COS += 1
         docs[doc].append(amount)
         cos[co].append(amount)
         #print doc, " ", co, " ", amount

   assert(NUM_COS == len(cos))
   assert(NUM_DOCS == len(docs))

   print "==== Results ===="
   print "Bad lines in file (lines excluded): %d" %(len(badLines))
   print "Num payments (good lines): %d" %(i - len(badLines))
   print "Num providers/docs: %d" %(len(docs))
   print "Num companies/payers: %d" %(len(cos))

   cosPaymentCountHist = genPaymentCountHistogram(cos)
   assert(NUM_COS == sum( cosPaymentCountHist.values() ))

   docsPaymentCountHist = genPaymentCountHistogram(docs)
   assert(NUM_DOCS == sum( docsPaymentCountHist.values() ))

   print "cos: Num payments, num companies making that many payments"
   for k in sorted(cosPaymentCountHist):
      print "%d %d" %(k, cosPaymentCountHist[k])

   print "docs: Num payments, num doctors recieving that many payments"
   for k in sorted(docsPaymentCountHist):
      print "%d %d" %(k, docsPaymentCountHist[k])

   cosSumPayments = sumPayments(cos)
   assert(NUM_COS == len(cosSumPayments))
   docsSumPayments = sumPayments(docs)
   assert(NUM_DOCS == len(docsSumPayments))

   binsize = 100.
   cosPaymentHist = paymentAmountHistogram(cosSumPayments, binsize)
   assert(NUM_COS == sum( cosPaymentHist.values() ))
   docsPaymentHist = paymentAmountHistogram(docsSumPayments, binsize)
   assert(NUM_DOCS == sum( docsPaymentHist.values() ))

   print "cos: Payment histogram: payment->+%f, num cos making that much in total payments" %(binsize)
   for k in sorted(cosPaymentHist):
      print "%f %d" %(k, cosPaymentHist[k])

   print "docs: Payment histogram: payment->+%f, num docs taking that much in total payments" %(binsize)
   for k in sorted(docsPaymentHist):
      print "%f %d" %(k, docsPaymentHist[k])


if __name__ == "__main__":
   "Generating statistics"
   filename = "payment_graph_physician_company.csv"
   printStats(filename)
