# CS465 at Johns Hopkins University.
# Module to estimate n-gram probabilities.

# Updated by Jason Baldridge <jbaldrid@mail.utexas.edu> for use in NLP
# course at UT Austin. (9/9/2008)

# Modified by Mozhi Zhang <mzhang29@jhu.edu> to add the new log linear model
# with word embeddings.  (2/17/2016)


import math
import random
import re
import sys
import scipy
import scipy.misc
import numpy as np

BOS = 'BOS'   # special word type for context at Beginning Of Sequence
EOS = 'EOS'   # special word type for observed token at End Of Sequence
OOV = 'OOV'    # special word type for all Out-Of-Vocabulary words
OOL = 'OOL'    # special word type for all Out-Of-Lexicon words
DEFAULT_TRAINING_DIR = "/usr/local/data/cs465/hw-lm/All_Training/"
OOV_THRESHOLD = 3  # minimum number of occurrence for a word to be considered in-vocabulary


# TODO for TA: Maybe we should use inheritance instead of condition on the
# smoother (similar to the Java code).
class LanguageModel:
  def __init__(self):
    # The variables below all correspond to quantities discussed in the assignment.
    # For log-linear or Witten-Bell smoothing, you will need to define some 
    # additional global variables.
    self.smoother = None       # type of smoother we're using
    self.lambdap = None        # lambda or C parameter used by some smoothers

    # The word vector for w can be found at self.vectors[w].
    # You can check if a word is contained in the lexicon using
    #    if w in self.vectors:
    self.vectors = None    # loaded using read_vectors()

    self.vocab = None    # set of words included in the vocabulary
    self.vocab_size = None  # V: the total vocab size including OOV.

    self.tokens = None      # the c(...) function
    self.types_after = None # the T(...) function

    self.progress = 0        # for the progress bar

    self.bigrams = None
    self.trigrams = None
    
    # the two weight matrices X and Y used in log linear model
    # They are initialized in train() function and represented as two
    # dimensional lists.
    self.X, self.Y = None, None  
    self.E = None

    # self.tokens[(x, y, z)] = # of times that xyz was observed during training.
    # self.tokens[(y, z)]    = # of times that yz was observed during training.
    # self.tokens[z]         = # of times that z was observed during training.
    # self.tokens[""]        = # of tokens observed during training.
    #
    # self.types_after[(x, y)]  = # of distinct word types that were
    #                             observed to follow xy during training.
    # self.types_after[y]       = # of distinct word types that were
    #                             observed to follow y during training.
    # self.types_after[""]      = # of distinct word types observed during training.

  def prob(self, x, y, z, is_file=False):
    """Computes a smoothed estimate of the trigram probability p(z | x,y)
    according to the language model.
    """

    if self.smoother == "UNIFORM":
      return float(1) / self.vocab_size
    elif self.smoother == "ADDL":
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      return ((self.tokens.get((x, y, z), 0) + self.lambdap) /
        (self.tokens.get((x, y), 0) + self.lambdap * self.vocab_size))

      # Notice that summing the numerator over all values of typeZ
      # will give the denominator.  Therefore, summing up the quotient
      # over all values of typeZ will give 1, so sum_z p(z | ...) = 1
      # as is required for any probability function.

    elif self.smoother == "BACKOFF_ADDL":
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      p_z = (self.tokens.get(z, 0) + self.lambdap) / (self.tokens.get('', 0) + self.lambdap * self.vocab_size)
      p_yz = (self.tokens.get((y, z), 0) + 
              self.lambdap * self.vocab_size * p_z) / (
                      self.tokens.get(y, 0) + self.lambdap * self.vocab_size)
      out = ((self.tokens.get((x, y, z), 0) + 
          self.lambdap * self.vocab_size * p_yz) / 
          (self.tokens.get((x, y), 0) + self.lambdap * self.vocab_size))
      return out
      #sys.exit("BACKOFF_ADDL is not implemented yet (that's your job!)")
    
    elif self.smoother == "BACKOFF_WB":
      sys.exit("BACKOFF_WB is not implemented yet (that's your job!)")

    elif self.smoother == "LOGLINEAR":
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      if x not in self.vectors:
        x = OOL
      if y not in self.vectors:
        y = OOL
      if z not in self.vectors:
        z = OOL
#      u_xyz = math.exp(self.vectors[x].transpose() * self.X * self.vectors[z] + 
#            self.vectors[y].transpose() * self.Y * self.vectors[z])
      log_u_xyz = (self.vectors[x].transpose() * self.X * self.vectors[z] + 
            self.vectors[y].transpose() * self.Y * self.vectors[z])
#      z_xy = np.exp(self.vectors[x].transpose() * self.X * self.E + self.vectors[y].transpose() * self.Y * self.E).sum()
      log_z_xy = scipy.misc.logsumexp(self.vectors[x].transpose() * self.X * self.E + self.vectors[y].transpose() * self.Y * self.E)
#      return u_xyz / z_xy
      if is_file:
        return float(log_u_xyz - log_z_xy)
      else:
        return float(math.exp(log_u_xyz - log_z_xy))
    #sys.exit("LOGLINEAR is not implemented yet (that's your job!)")
    
    elif self.smoother == "LOGLINEAR_IMPROV":
      if x not in self.vocab:
        x = OOV
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      if x not in self.vectors:
        x = OOL
      if y not in self.vectors:
        y = OOL
      if z not in self.vectors:
        z = OOL
#      u_xyz = math.exp(self.vectors[x].transpose() * self.X * self.vectors[z] + 
#            self.vectors[y].transpose() * self.Y * self.vectors[z])
      log_u_xyz = (self.vectors[x].transpose() * self.X * self.vectors[z] + self.vectors[y].transpose() * self.Y * self.vectors[z] + self.beta * math.log(self.tokens.get(z, 0)+1))
#      log_u_xyz = (self.vectors[x].transpose() * self.X * self.vectors[z] + self.vectors[y].transpose() * self.Y * self.vectors[z])
#      z_xy = np.exp(self.vectors[x].transpose() * self.X * self.E + self.vectors[y].transpose() * self.Y * self.E).sum()
      log_z_xy = scipy.misc.logsumexp(self.vectors[x].transpose() * self.X * self.E + self.vectors[y].transpose() * self.Y * self.E + self.beta * self.K)
#      return u_xyz / z_xy
      if is_file:
        #print(self.beta, self.tokens.get(z,0), log_u_xyz, log_z_xy, log_u_xyz - log_z_xy)
        return float(log_u_xyz - log_z_xy)
      else:
        return float(math.exp(log_u_xyz - log_z_xy))
    #sys.exit("LOGLINEAR is not implemented yet (that's your job!)")

    else:
      sys.exit("%s has some weird value" % self.smoother)
  

  def prob_2gram(self,y,z):
    """Computes a smoothed estimate of the bigram probability p(z|y)
    according to the language model.
    """
    if self.smoother == "UNIFORM":
      return float(1) / self.vocab_size
    elif self.smoother == "ADDL":
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      return ((self.tokens.get((y, z), 0) + self.lambdap) /
        (self.tokens.get((y), 0) + self.lambdap * self.vocab_size))

      # Notice that summing the numerator over all values of typeZ
      # will give the denominator.  Therefore, summing up the quotient
      # over all values of typeZ will give 1, so sum_z p(z | ...) = 1
      # as is required for any probability function.

    elif self.smoother == "BACKOFF_ADDL":
      if y not in self.vocab:
        y = OOV
      if z not in self.vocab:
        z = OOV
      p_z = (self.tokens.get(z, 0) + self.lambdap) / (self.tokens.get('', 0) + self.lambdap * self.vocab_size)
      return ((self.tokens.get((y, z), 0) +
          self.lambdap * self.vocab_size * p_z) /
          (self.tokens.get((y), 0) + self.lambdap * self.vocab_size))
      #sys.exit("BACKOFF_ADDL is not implemented yet (that's your job!)")

    elif self.smoother == "BACKOFF_WB":
      sys.exit("BACKOFF_WB is not implemented yet (that's your job!)")


    else:
      sys.exit("%s has some weird value" % self.smoother)

  def prob_1gram(self,z):
    """Computes a smoothed estimate of the bigram probability p(z|y)
    according to the language model.
    """
    if self.smoother == "UNIFORM":
      return float(1) / self.vocab_size
    elif self.smoother == "ADDL":
      if z not in self.vocab:
        z = OOV
      return ((self.tokens.get((z), 0) + self.lambdap) /
        (self.lambdap * self.vocab_size))

      # Notice that summing the numerator over all values of typeZ
      # will give the denominator.  Therefore, summing up the quotient
      # over all values of typeZ will give 1, so sum_z p(z | ...) = 1
      # as is required for any probability function.

    elif self.smoother == "BACKOFF_ADDL":
      if z not in self.vocab:
        z = OOV
      p_z = (self.tokens.get(z, 0) + self.lambdap) / (self.tokens.get('', 0) + self.lambdap * self.vocab_size)
      return ((self.tokens.get((y, z), 0) +
          self.lambdap * self.vocab_size * p_z) /
          (self.tokens.get((y), 0) + self.lambdap * self.vocab_size))
      #sys.exit("BACKOFF_ADDL is not implemented yet (that's your job!)")

    elif self.smoother == "BACKOFF_WB":
      sys.exit("BACKOFF_WB is not implemented yet (that's your job!)")


    else:
      sys.exit("%s has some weird value" % self.smoother)


  def filelogprob(self, filename):
    """Compute the log probability of the sequence of tokens in file.
    NOTE: we use natural log for our internal computation.  You will want to
    divide this number by log(2) when reporting log probabilities.
    """
    logprob = 0.0
    x, y = BOS, BOS
    corpus = self.open_corpus(filename)
    for line in corpus:
      for z in line.split():
        if self.smoother[:9] == 'LOGLINEAR':
          prob = self.prob(x, y, z, is_file=True)
          logprob += prob
        else:
          prob = self.prob(x, y, z)
          logprob += math.log(prob)
        x = y
        y = z
    if self.smoother[:9] == 'LOGLINEAR':
      logprob += self.prob(x, y, EOS, is_file=True)
    else:
      logprob += math.log(self.prob(x, y, EOS))
    corpus.close()
    return logprob

  def read_vectors(self, filename):
    """Read word vectors from an external file.  The vectors are saved as
    arrays in a dictionary self.vectors.
    """
    with open(filename) as infile:
      header = infile.readline()
      self.dim = int(header.split()[-1])
      self.vectors = {}
      for line in infile:
        arr = line.split()
        word = arr.pop(0)
        self.vectors[word] = np.mat([float(x) for x in arr]).transpose()

  def train (self, filename):
    """Read the training corpus and collect any information that will be needed
    by the prob function later on.  Tokens are whitespace-delimited.

    Note: In a real system, you wouldn't do this work every time you ran the
    testing program. You'd do it only once and save the trained model to disk
    in some format.
    """
    sys.stderr.write("Training from corpus %s\n" % filename)

    # Clear out any previous training
    self.tokens = { }
    self.types_after = { }
    self.unigrams = []
    self.bigrams = []
    self.trigrams = [];
  
    # While training, we'll keep track of all the trigram and bigram types
    # we observe.  You'll need these lists only for Witten-Bell backoff.
    # The real work:
    # accumulate the type and token counts into the global hash tables.

    # If vocab size has not been set, build the vocabulary from training corpus
    if self.vocab_size is None:
      self.set_vocab_size(filename)

    # We save the corpus in memory to a list tokens_list.  Notice that we
    # appended two BOS at the front of the list and a EOS at the end.  You
    # will need to add more BOS tokens if you want to use a longer context than
    # trigram.
    x, y = BOS, BOS  # Previous two words.  Initialized as "beginning of sequence"
    # count the BOS context
    self.tokens[(x, y)] = 1
    self.tokens[y] = 1

    tokens_list = [x, y]  # the corpus saved as a list
    corpus = self.open_corpus(filename)
    for line in corpus:
      for z in line.split():
        # substitute out-of-vocabulary words with OOV symbol
        if z not in self.vocab:
          z = OOV
        # substitute out-of-lexicon words with OOL symbol (only for log-linear models)
        if self.smoother[:9] == 'LOGLINEAR' and z not in self.vectors:
          z = OOL
        self.count(x, y, z)
        self.show_progress()
        x=y; y=z
        tokens_list.append(z)
    tokens_list.append(EOS)   # append a end-of-sequence symbol 
    sys.stderr.write('\n')    # done printing progress dots "...."
    self.count(x, y, EOS)     # count EOS "end of sequence" token after the final context
    corpus.close()
    if self.smoother == 'LOGLINEAR': 
      # Train the log-linear model using SGD.

      # Initialize parameters
      #self.X = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]
      #self.Y = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]
      self.X = np.mat(np.zeros([self.dim, self.dim]))
      self.Y = np.mat(np.zeros([self.dim, self.dim]))
      self.E = np.mat(np.zeros([self.dim, self.vocab_size]))

      for index, value in enumerate(self.vocab):
        if value not in self.vectors:
          value = OOL
        self.E[:,index] = self.vectors[value]

      # Optimization parameters
      gamma0 = self.gamma0  # initial learning rate, used to compute actual learning rate
      epochs = self.epochs  # number of passes

      self.N = len(tokens_list) - 2  # number of training instances

      # ******** COMMENT *********
      # In log-linear model, you will have to do some additional computation at
      # this point.  You can enumerate over all training trigrams as following.
      #
      # for i in range(2, len(tokens_list)):
      #   x, y, z = tokens_list[i - 2], tokens_list[i - 1], tokens_list[i]
      #
      # Note1: self.lambdap is the regularizer constant C
      # Note2: You can use self.show_progress() to log progress.
      #
      # **************************


      #####################
      # TODO: Implement your SGD here
      #sys.stderr.write("Vocabulary size is %d types including OOV and EOS.\n" % len(self.vectors))
      t = 0
      gamma = gamma0
      for epoch in xrange(epochs):
        for i in xrange(2, len(tokens_list)):
          gamma = gamma0 / (1 + gamma0 * 2 * self.lambdap / self.N * t)

          x, y, z = tokens_list[i - 2], tokens_list[i - 1], tokens_list[i]
#          z_xy_ = np.exp(self.vectors[x].transpose() * self.X * self.E + 
#                  self.vectors[y].transpose() * self.Y * self.E)
          log_z_xy_ = (self.vectors[x].transpose() * self.X * self.E + 
                  self.vectors[y].transpose() * self.Y * self.E)
          log_z_xy_sum = scipy.misc.logsumexp(log_z_xy_)
#          second_term = (z_xy_ * self.E.transpose()) / z_xy_.sum()
          second_term = (np.exp(log_z_xy_ - log_z_xy_sum)* self.E.transpose())
          grad_X = self.vectors[x] * self.vectors[z].transpose() - self.vectors[x] * second_term - 2 * self.lambdap / self.N * self.X
          grad_Y = self.vectors[y] * self.vectors[z].transpose() - self.vectors[y] * second_term - 2 * self.lambdap / self.N * self.Y
          self.show_progress()
          
          # check gradient computation
          is_check = 0
          if i % 300 == 0 and is_check:
            random_X = 0.000001 * np.random.ranf(self.X.shape)
            random_Y = 0.000001 * np.random.ranf(self.Y.shape)
            F_i = math.log(self.prob(x, y, z)) - self.lambdap/self.N*(np.multiply(self.X,self.X).sum()+np.multiply(self.Y,self.Y).sum())
            self.X = self.X + random_X
            self.Y = self.Y + random_Y
            F_i_post = math.log(self.prob(x, y, z)) - self.lambdap/self.N*(np.multiply(self.X,self.X).sum()+np.multiply(self.Y,self.Y).sum())
            F_rhs = np.multiply(random_X, grad_X).sum() + np.multiply(random_Y, grad_Y).sum()
            sys.stderr.write("%d %d %.10f \n" % (epoch, i, F_i_post-F_i-F_rhs))
            self.X = self.X - random_X
            self.Y = self.Y - random_Y
            probs = [self.prob(x,y,v) for v in self.vocab]
            sys.stderr.write('prob distribution on vacab: '+str(probs)+'\n')
            sys.stderr.write('sum to: '+str(np.array(probs).sum())+'\n')
              

          self.X = self.X + gamma * grad_X
          self.Y = self.Y + gamma * grad_Y
          t += 1
        prob_gen = self.filelogprob(filename)
        F = (prob_gen  - self.lambdap * 
                (np.multiply(self.X, self.X).sum() + np.multiply(self.Y, self.Y).sum())) / self.N
        sys.stderr.write("epoch" + str(epoch+1) + ": F=" + str(float(F)) +"\n")
      #####################

    if self.smoother == 'LOGLINEAR_IMPROV': 
      # Train the log-linear model using SGD.

      # Initialize parameters
      #self.X = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]
      #self.Y = [[0.0 for _ in range(self.dim)] for _ in range(self.dim)]
      self.X = np.mat(np.zeros([self.dim, self.dim]))
      self.Y = np.mat(np.zeros([self.dim, self.dim]))
      self.beta = 0
      self.E = np.mat(np.zeros([self.dim, self.vocab_size]))
      self.K = np.mat(np.zeros([1,self.vocab_size]))

      for index, value in enumerate(self.vocab):
        if value not in self.vectors:
          value = OOL
        self.E[:,index] = self.vectors[value]
        self.K[0,index] = math.log(self.tokens.get(value, 0)+1)
        #self.K[0,index] = 0

      # Optimization parameters
      gamma0 = self.gamma0  # initial learning rate, used to compute actual learning rate
      epochs = self.epochs  # number of passes

      self.N = len(tokens_list) - 2  # number of training instances

      # ******** COMMENT *********
      # In log-linear model, you will have to do some additional computation at
      # this point.  You can enumerate over all training trigrams as following.
      #
      # for i in range(2, len(tokens_list)):
      #   x, y, z = tokens_list[i - 2], tokens_list[i - 1], tokens_list[i]
      #
      # Note1: self.lambdap is the regularizer constant C
      # Note2: You can use self.show_progress() to log progress.
      #
      # **************************


      #####################
      # TODO: Implement your SGD here
      #sys.stderr.write("Vocabulary size is %d types including OOV and EOS.\n" % len(self.vectors))
      t = 0
      gamma = gamma0
      for epoch in xrange(epochs):
        for i in xrange(2, len(tokens_list)):
          gamma = gamma0 / (1 + gamma0 * 2 * self.lambdap / self.N * t)

          x, y, z = tokens_list[i - 2], tokens_list[i - 1], tokens_list[i]
#          z_xy_ = np.exp(self.vectors[x].transpose() * self.X * self.E + 
#                  self.vectors[y].transpose() * self.Y * self.E)
          log_z_xy_ = (self.vectors[x].transpose() * self.X * self.E + 
                  self.vectors[y].transpose() * self.Y * self.E)
#          sys.stderr.write(str(log_z_xy_.shape)+' '+str((self.beta*self.K).shape)+'\n')
          log_z_xy_ = log_z_xy_ + self.beta * self.K
          log_z_xy_sum = scipy.misc.logsumexp(log_z_xy_)
#          second_term = (z_xy_ * self.E.transpose()) / z_xy_.sum()
          second_term = (np.exp(log_z_xy_ - log_z_xy_sum)* self.E.transpose())
          grad_X = self.vectors[x] * self.vectors[z].transpose() - self.vectors[x] * second_term - 2 * self.lambdap / self.N * self.X
          grad_Y = self.vectors[y] * self.vectors[z].transpose() - self.vectors[y] * second_term - 2 * self.lambdap / self.N * self.Y
          grad_beta = math.log(self.tokens.get(z, 0)+1) - np.exp(log_z_xy_-log_z_xy_sum) * self.K.transpose() - 2 * self.lambdap / self.N * self.beta
          #grad_beta = 0 - np.exp(log_z_xy_) * self.K.transpose() - 2 * self.lambdap / self.N * self.beta
          self.show_progress()
          
          # check gradient computation
          is_check = 0
          if i % 300 == 0 and is_check:
            random_X = 0.000001 * np.random.ranf(self.X.shape)
            random_Y = 0.000001 * np.random.ranf(self.Y.shape)
            random_beta = 0.000001 * np.random.ranf()
            F_i = self.prob(x, y, z, is_file=True) - self.lambdap/self.N*(np.multiply(self.X,self.X).sum()+np.multiply(self.Y,self.Y).sum()+self.beta*self.beta)
            self.X = self.X + random_X
            self.Y = self.Y + random_Y
            self.beta = self.beta + random_beta
            F_i_post = self.prob(x, y, z, is_file=True) - self.lambdap/self.N*(np.multiply(self.X,self.X).sum()+np.multiply(self.Y,self.Y).sum()+self.beta*self.beta)
            F_rhs = np.multiply(random_X, grad_X).sum() + np.multiply(random_Y, grad_Y).sum() + random_beta * grad_beta
            sys.stderr.write("%d %d %.10f \n" % (epoch, i, F_i_post-F_i-F_rhs))
            self.X = self.X - random_X
            self.Y = self.Y - random_Y
            self.beta = self.beta - random_beta
            #probs = [self.prob(x,y,v) for v in self.vocab]
            #sys.stderr.write('prob distribution on vacab: '+str(probs)+'\n')
            #sys.stderr.write('sum to: '+str(np.array(probs).sum())+'\n')
              

          self.X = self.X + gamma * grad_X
          self.Y = self.Y + gamma * grad_Y
          self.beta = self.beta + gamma * grad_beta
          t += 1
        prob_gen = self.filelogprob(filename)
        F = (prob_gen  - self.lambdap * 
                (np.multiply(self.X, self.X).sum() + np.multiply(self.Y, self.Y).sum() + self.beta*self.beta)) / self.N
        sys.stderr.write("epoch" + str(epoch+1) + ": F=" + str(float(F)) +"\n")
      #####################

    sys.stderr.write("Finished training on %d tokens\n" % self.tokens[""])

  def count(self, x, y, z):
    """Count the n-grams.  In the perl version, this was an inner function.
    For now, I am just using a class variable to store the found tri-
    and bi- grams.
    """
    self.tokens[(x, y, z)] = self.tokens.get((x, y, z), 0) + 1
    if self.tokens[(x, y, z)] == 1:       # first time we've seen trigram xyz
      self.trigrams.append((x, y, z))
      self.types_after[(x, y)] = self.types_after.get((x, y), 0) + 1

    self.tokens[(y, z)] = self.tokens.get((y, z), 0) + 1
    if self.tokens[(y, z)] == 1:        # first time we've seen bigram yz
      self.bigrams.append((y, z))
      self.types_after[y] = self.types_after.get(y, 0) + 1

    self.tokens[z] = self.tokens.get(z, 0) + 1
    if self.tokens[z] == 1:         # first time we've seen unigram z
      self.types_after[''] = self.types_after.get('', 0) + 1
    #  self.vocab_size += 1

    self.tokens[''] = self.tokens.get('', 0) + 1  # the zero-gram


  def set_vocab_size(self, *files):
    """When you do text categorization, call this function on the two
    corpora in order to set the global vocab_size to the size
    of the single common vocabulary.

     """
    count = {} # count of each word

    for filename in files:
      corpus = self.open_corpus(filename)
      for line in corpus:
        for z in line.split():
          count[z] = count.get(z, 0) + 1
          self.show_progress();
      corpus.close()
    self.vocab = set(w for w in count if count[w] >= OOV_THRESHOLD)

    self.vocab.add(OOV)  # add OOV to vocab
    self.vocab.add(EOS)  # add EOS to vocab (but not BOS, which is never a possible outcome but only a context)
    sys.stderr.write('\n')    # done printing progress dots "...."

    if self.vocab_size is not None:
      sys.stderr.write("Warning: vocab_size already set; set_vocab_size changing it\n")
    self.vocab_size = len(self.vocab)
    sys.stderr.write("Vocabulary size is %d types including OOV and EOS\n"
                      % self.vocab_size)

  def set_smoother(self, arg):
    """Sets smoother type and lambda from a string passed in by the user on the
    command line.
    """
    r = re.compile('^(.*?)-?([0-9.]*)$')
    m = r.match(arg)
    
    if not m.lastindex:
      sys.exit("Smoother regular expression failed for %s" % arg)
    else:
      smoother_name = m.group(1)
      if m.lastindex >= 2 and len(m.group(2)):
        lambda_arg = m.group(2)
        self.lambdap = float(lambda_arg)
      else:
        self.lambdap = None

    self.gamma0 = 0.01
    self.epochs = 10
    if smoother_name.lower() == 'uniform':
      self.smoother = "UNIFORM"
    elif smoother_name.lower() == 'add':
      self.smoother = "ADDL"
    elif smoother_name.lower() == 'backoff_add':
      self.smoother = "BACKOFF_ADDL"
    elif smoother_name.lower() == 'backoff_wb':
      self.smoother = "BACKOFF_WB"
    elif smoother_name.lower() == 'loglinear':
      self.smoother = "LOGLINEAR"
    elif smoother_name.lower() == 'loglinear_improv':
      self.smoother = "LOGLINEAR_IMPROV"
    elif smoother_name.lower() == 'improved':
      self.smoother = "LOGLINEAR_IMPROV"
      self.lambdap = 14.0
      self.gamma0 = 0.01
      self.epochs = 20
    else:
      sys.exit("Don't recognize smoother name '%s'" % smoother_name)
    
    if self.lambdap is None and self.smoother.find('ADDL') != -1:
      sys.exit('You must include a non-negative lambda value in smoother name "%s"' % arg)

  def open_corpus(self, filename):
    """Associates handle CORPUS with the training corpus named by filename."""
    try:
      corpus = open(filename, "r")
    except IOError as err:
      try:
        corpus = open(DEFAULT_TRAINING_DIR + filename, "r")
      except IOError as err:
        sys.exit("Couldn't open corpus at %s or %s" % (filename,
                 DEFAULT_TRAINING_DIR + filename))
    return corpus

  def num_tokens(self, filename):
    corpus = self.open_corpus(filename)
    num_tokens = sum([len(l.split()) for l in corpus]) + 1

    return num_tokens

  def show_progress(self, freq=5000):
    """Print a dot to stderr every 5000 calls (frequency can be changed)."""
    self.progress += 1
    if self.progress % freq == 1:
      sys.stderr.write('.')

  @classmethod
  def load(cls, fname):
    try:
      import cPickle as pickle
    except:
      import pickle
    fh = open(fname, mode='rb')
    loaded = pickle.load(fh)
    fh.close()
    return loaded

  def save(self, fname):
    try:
      import cPickle as pickle
    except:
      import pickle
    with open(fname, mode='wb') as fh:
      pickle.dump(self, fh, protocol=pickle.HIGHEST_PROTOCOL)

