'''

Bryan Lewandowski

Generate basic stats about the payment_graph_physician_company.csv
data.
'''


'''
Produce a count histogram.
Input: a dict: int -> [float(actually any)], which is a doctor to a list of
      payments.
Output: a dict: int -> int, which is a integer number of payments to the
      number of doctors who received that many payments.
'''
def genCountHistogram(d):
   hist = dict()
   for k in d:
      numPayments = len(d[k])
      if numPayments not in hist:
         hist[numPayments] = 0
      hist[numPayments] += 1
   return hist


def printStats(filename):
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
         if co not in cos:
            cos[co] = []
         docs[doc].append(amount)
         cos[co].append(amount)
         #print doc, " ", co, " ", amount

   print "==== Results ===="
   print "Bad lines in file (lines excluded): %d" %(len(badLines))
   print "Num providers/docs: %d" %(len(docs))
   print "Num companies/payers: %d" %(len(cos))

   cosCountHist = genCountHistogram(cos)
   docsCountHist = genCountHistogram(docs)

   print "cos: Payments, num companies making that many payments"
   for k in sorted(cosCountHist):
      print "%d %d" %(k, cosCountHist[k])


   print "docs: Payments, num doctors recieving that many payments"
   for k in sorted(docsCountHist):
      print "%d %d" %(k, docsCountHist[k])


if __name__ == "__main__":
   "Generating statistics"
   filename = "payment_graph_physician_company.csv"
   printStats(filename)
