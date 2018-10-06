#!/usr/bin/env python

# Sample program for hw-lm
# CS465 at Johns Hopkins University.

# Converted to python by Eric Perlman <eric@cs.jhu.edu>

# Updated by Jason Baldridge <jbaldrid@mail.utexas.edu> for use in NLP
# course at UT Austin. (9/9/2008)

# Modified by Mozhi Zhang <mzhang29@jhu.edu> to add the new log linear model
# with word embeddings.  (2/17/2016)

from __future__ import print_function

import math
import sys

import Probs

# Computes the log probability of the sequence of tokens in file,
# according to a trigram model.  The training source is specified by
# the currently open corpus, and the smoothing method used by
# prob() is specified by the global variable "smoother". 

def get_model_filename(smoother, lexicon, train_file):
    import hashlib
    from os.path import basename
    train_hash = basename(train_file)
    lexicon_hash = basename(lexicon)
    filename = '{}_{}_{}.model'.format(smoother, lexicon_hash, train_hash)
    return filename

def main():
  course_dir = '/usr/local/data/cs465/'

  if len(sys.argv) < 6 or (sys.argv[1] == 'TRAIN' and len(sys.argv) != 6):
    print("""
Prints the log-probability of each file under a smoothed n-gram model.

Usage:   {} TRAIN smoother lexicon trainpath
         {} TEST smoother lexicon trainpath files...
Example: {} TRAIN add0.01 {}hw-lm/lexicons/words-10.txt switchboard-small
         {} TEST add0.01 {}hw-lm/lexicons/words-10.txt switchboard-small {}hw-lm/speech/sample*

Possible values for smoother: uniform, add1, backoff_add1, backoff_wb, loglinear1
  (the \"1\" in add1/backoff_add1 can be replaced with any real lambda >= 0
   the \"1\" in loglinear1 can be replaced with any C >= 0 )
lexicon is the location of the word vector file, which is only used in the loglinear model
trainpath is the location of the training corpus
  (the search path for this includes "{}")
""".format(sys.argv[0], sys.argv[0], sys.argv[0], course_dir, sys.argv[0], course_dir, course_dir, Probs.DEFAULT_TRAINING_DIR))
    sys.exit(1)

  mode = sys.argv[1]
  argv = sys.argv[2:]

  smoother = argv.pop(0)
  lexicon = argv.pop(0)
  train_file1 = argv.pop(0)
  train_file2 = argv.pop(0)

  if mode == 'TRAIN':

    lm = Probs.LanguageModel()
    lm.set_vocab_size(train_file1, train_file2)
    lm.set_smoother(smoother)
    lm.read_vectors(lexicon)
    lm.train(train_file1)
    lm.save(get_model_filename(smoother, lexicon, train_file1))

    lm.train(train_file2)
    lm.save(get_model_filename(smoother, lexicon, train_file2))

  elif mode == 'TEST':
    if len(argv) < 2:
      print("warning: not enough")
    lm1 = Probs.LanguageModel.load(get_model_filename(smoother, lexicon, train_file1))
    lm2 = Probs.LanguageModel.load(get_model_filename(smoother, lexicon, train_file2))
    # We use natural log for our internal computations and that's
    # the kind of log-probability that fileLogProb returns.  
    # But we'd like to print a value in bits: so we convert
    # log base e to log base 2 at print time, by dividing by log(2).
    prior_gen = argv.pop(0)
    prior_gen = float(prior_gen)
    
    #file_len_acc = open("len_acc.txt","w")
    total_cross_1 = 0.
    total_cross_2 = 0.
    

    sum_acc1 = 0.
    sum_acc2 = 0.

    count_1 = 0
    count_2 = 0
    file_count = 0
    for testfile in argv:
      file_count += 1

      log_prior_1 = math.log(prior_gen,2)  
      ce1 = lm1.filelogprob(testfile) / math.log(2)
      log_posterior_1 = ce1 + log_prior_1

      log_prior_2 = math.log(1-prior_gen,2)
      ce2 = lm2.filelogprob(testfile) / math.log(2)
      log_posterior_2 = ce2 + log_prior_2

      total_cross_1 -= ce1
      total_cross_2 -= ce2
#      total_cross_1 -= log_posterior_1
#      total_cross_2 -= log_posterior_2

      
      if log_posterior_1 > log_posterior_2:
        #print(train_file1 + "\t" + testfile + "\n")
        count_1 += 1
      else:
        #print(train_file2 + "\t" + testfile + "\n")
        count_2 += 1
      
      #filename_spt = testfile.split("/")
      #length = filename_spt[2].split(".")[1]


      CON = max(0-log_posterior_1, 0-log_posterior_2)
      try:
          p1 = pow(2,log_posterior_1+CON)
          p2 = pow(2,log_posterior_2+CON)
          
          acc1 = p1/(p1+p2)
          acc2 = p2/(p1+p2)
          
          #print(acc1)
          #print(acc2)

          sum_acc1 += acc1
          sum_acc2 += acc2

      except Exception as e:
          #print(e)
          
          if log_posterior_1 > log_posterior_2:
              sum_acc1 += 1
              
          else:
              sum_acc2 += 1
    

    setname = testfile.split("/")[-3]
    
    if setname == "english":
        print(sum_acc1)
        print(total_cross_1)

    elif setname == "spanish":
        print(sum_acc2)
        print(total_cross_2)

    print(file_count)
    print(sum([lm1.num_tokens(testfile) for testfile in argv]))
      
    if setname == "english":
        print(count_1)

    elif setname == "spanish":
        print(count_2)
    
    
        

      #if filename_spt[1] == train_file1:

          #file_len_acc.write(length+" "+str(log_posterior_1)+"\n")
      
      #elif filename_spt[1] == train_file2:

          #file_len_acc.write(length+" "+str(log_posterior_2)+"\n")
        
    #file_len_acc.close()

    prob1 = round((float(count_1)/float(count_1+count_2))*100,2)
    prob2 = round((float(count_2)/float(count_1+count_2))*100,2)




    #print(str(count_1) + " files were more probably " + train_file1 +" (" + str(prob1) +"%)\n")
    #print(str(count_2) + " files were more probably " + train_file2 +" (" + str(prob2) +"%)\n")
  else:
    sys.exit(-1)

if __name__ ==  "__main__":
  main()

