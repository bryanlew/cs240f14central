'''
splitMerge.py
(do an external merge sort)
'''

import os
import math
import itertools
from subprocess import call



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
Write out a chunk into fout, the set of (docID, docID) tuples in partSet,
with a tab between them.  Also add a header comment line to the file.
'''
def writeChunk(fout, partSet):
   print "Writing chunk "+str(fout.name)
   fout.write("# doctorId   doctorId\n")
   for s in sorted(partSet):
      writeTab(fout, s[0], s[1])

   
'''
Open a file named wholeFileN, discard the first line (assumed to be a
header), and then partition the remaining lines into four chunks.
Based on knowing the input file format, these chunks are built
sequentially rather than round-robin.
Returns a list of the file names the chunks were saved under
'''
def partitionAndRemoveDups(wholefileN, NUM_PARTITIONS):
   chunks = []

   # Heuristic for chunk size- don't want to round-robin.
   wholeFileBytes = os.stat(wholefileN).st_size
   # Chunk end: file.tell() > curChunk * wholeFileBytes / NUM_PARTITIONS
   curChunk = 1
   chunkName = wholefileN+"_chunk"+str(curChunk)
   chunks.append(chunkName)
   curChunkF = open(chunkName, "w")

   partSet = set() # set (docId, docID) pairs, sorted so min docId is 1st.

   with open(wholefileN) as fin:
      curLine = 0
      for line in fin:
         curLine += 1
         if curLine == 1:
            continue # skip header/comment line
         if (curLine % 1000000) == 0:
            print "Read %f %% of input" %(fin.tell()*100./float(wholeFileBytes))

         # New chunk?
         if fin.tell() > curChunk * wholeFileBytes / NUM_PARTITIONS:
            writeChunk(curChunkF, partSet)
            curChunkF.close()
            curChunk += 1
            print "New chunk: %d" %(curChunk)
            chunkName = wholefileN+"_chunk"+str(curChunk)
            chunks.append(chunkName)
            curChunkF = open(chunkName, "w")
            partSet = set()
         s = line.split()
         assert(len(s) == 2)
         partSet.add(( min(s[0],s[1]), max(s[0],s[1]) ))

   writeChunk(curChunkF, partSet)
   curChunkF.close()

   assert(len(chunks) == NUM_PARTITIONS)
   return chunks


'''
A ChunkReader is an interface to the head element of a chunk file.
Used by mergeChunks.
'''
class ChunkReader:
   def __init__(self, chunkfileName):
      self.fn = chunkfileName
      self.fin = open(chunkfileName, "r")
      # Discard the first header line
      self.fin.readline()
      self.nextEntry = None

   def close(self):
      self.fin.close()

   def nextLine(self):
      try:
         line = self.fin.readline()
         s = line.split()
         self.nextEntry = (int(s[0]), int(s[1]))
      except IOError as e:
         print "IOError on read (chunk done?): " + e.strerror
         self.nextEntry = None
         self.close()

   def head(self):
      return self.nextEntry


'''
Given a final output file name and a list of chunk filenames, merge the
chunks into one output file, and eliminate duplicates.
'''
def mergeChunks(finaloutputfileN, chunksN):
   assert(finaloutputfileN != "")
   assert(len(chunksN) > 0)

   # Open the chunks
   chunks = []
   for fname in chunksN:
      cr = ChunkReader(fname)
      # Seed the chunk
      cr.nextLine()
      assert(cr.head() != None)
      chunks.append(cr)

   # TODO debug remove
   for c in chunks:
      print " option: " + str(c.head())

   # Find the minimum index and value at that index
   v, i = min((v.head(), i) for (i, v) in enumerate(chunks))
   print "chose value " +str(v) + " index "+str(i)
   assert(False)


if __name__ == "__main__":
   print "External sort merge (for the purpose of duplicate elimination)"
   
   wholefileN = "doc_doc_prop_doc_0.25_co_1e-05_.tab"
   # Split the wholefile into a list of chunks.
   # "chunks" is a list of filenames containing sorted, duplicate-removed
   # files.
   NUM_PARTITIONS = 20
   print "Partitioning into %d partitions..." %(NUM_PARTITIONS)
   #TODO restore (already did this run):
   #chunks = partitionAndRemoveDups(wholefileN, NUM_PARTITIONS)
   
   print "Merging partitions..."
   finaloutputfileN = wholefileN+".nodups.tab"
   
   # TODO temp remove this: did the chunks in a previous run
   chunks = []
   for i in range(1,21):
      n = "doc_doc_prop_doc_0.25_co_1e-05_.tab_chunk"+str(i)
      chunks.append(n)
   assert(len(chunks) == NUM_PARTITIONS)

   mergeChunks(finaloutputfileN, chunks)

   









