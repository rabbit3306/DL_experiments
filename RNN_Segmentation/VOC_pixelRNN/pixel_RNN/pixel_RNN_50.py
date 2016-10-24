"""
1. read IDs.txt file in, and separate as train, validation, test.
2. validation is not use for update parameter, just use to check lost function, and 
    compare with train lost function, to see over-fitting or under-fitting.
3. Four corners Done.
4. Before they only add the hidden layer together. Now I use concatenate to crop the 4 
    hidden layers together, and by doing CNN to mix all 4 layers information. 
5. with random.seed(123), it's not real random now...
6. Two corners, 2s for one image (48*48). Four coners, 4s. 
7. Use GPU, then should store in float32, sometimes the input need restore, so should
    "allow_input_downcast=True"

@Zhewei
10/20/2016

"""

import sys
import scipy.io
import numpy
import math
from PIL import Image
from random import shuffle
import random
numpy.random.seed(123)
random.seed(123)

import theano
import theano.tensor as T
import lib
import lasagne
import scipy.misc

import time
import functools
import itertools
import matplotlib.image as mpimg
import datetime

MODEL = 'pixel_rnn' # either pixel_rnn or pixel_cnn

# Hyperparams
BATCH_SIZE = 1
DIM = 64 # Model dimensionality.
GRAD_CLIP = 1 # Elementwise grad clip threshold

# Dataset
N_CHANNELS = 3
dataNo = 500
WIDTH = 50
HEIGHT = 50

# Other constants
TEST_BATCH_SIZE = 1 # batch size to use when evaluating on dev/test sets. This should be the max that can fit into GPU memory.
EVAL_DEV_COST = True # whether to evaluate dev cost during training
GEN_SAMPLES = True # whether to generate samples during training (generating samples takes WIDTH*HEIGHT*N_CHANNELS full passes through the net)
TRAIN_MODE = 'iters' # 'iters' to use PRINT_ITERS and STOP_ITERS, 'time' to use PRINT_TIME and STOP_TIME
PRINT_ITERS = 1 # Print cost, generate samples, save model checkpoint every N iterations.
                  #PRINT_ITERS is useless now.
STOP_ITERS = 5 # Stop after this many iterations
                  # Each means shuffle training data and continue to train
PRINT_TIME = 60*60 # Print cost, generate samples, save model checkpoint every N seconds.
STOP_TIME = 60*60*2 # Stop after this many seconds of actual training (not including time req'd to generate samples etc.)

lib.utils.print_model_settings(locals().copy())


def prepareData(IDList):

    data = numpy.zeros((dataNo, HEIGHT*WIDTH))
    for i in range(dataNo):
        tag_data = "~/data/VOCdevkit/VOC2012/JPEGImages/"+str(IDList[i])+'.jpg'
        pngfile = Image.open(tag_data)
        pix = pngfile.load()
        pixelValue = numpy.zeros((HEIGHT, WIDTH))
        for h in range(HEIGHT):
            for w in range(WIDTH):
                pixelValue[h,w] = pix[h,w]/256
        pixelValue = pixelValue.reshape(HEIGHT*WIDTH)
        data[i-1,:] = pixelValue
    
    target = numpy.zeros((dataNo, HEIGHT*WIDTH))
    for i in range(dataNo):
        tag_target = "~/data/VOC_Preprocessed_Data/SegmentationClass/50_50/"+str(IDList[i])+'.png'
        pngfile = Image.open(tag_target)
        pix = pngfile.load()
        pixelValue = numpy.zeros((HEIGHT, WIDTH))
        for h in range(HEIGHT):
            for w in range(WIDTH):
                pixelValue[h,w] = pix[h,w]/256
        pixelValue = pixelValue.reshape(HEIGHT*WIDTH)
        target[i-1,:] = pixelValue

    print (data.shape,target.shape)


    dataOrder = [i for i in range(data.shape[0])]
    shuffle(dataOrder)

    # train:validation:test = 8:1:1
    trainNo = math.floor(0.8*data.shape[0])
    validNo = math.floor(0.1*data.shape[0])
    trainNo = int(trainNo)
    validNo = int(validNo)
    trainData = data[dataOrder[0:trainNo], :]
    validData = data[dataOrder[trainNo:trainNo+validNo], :]
    testData = data[dataOrder[trainNo+validNo:], :]

    trainTarget = target[dataOrder[0:trainNo], :]
    validTarget = target[dataOrder[trainNo:trainNo+validNo], :]
    testTarget = target[dataOrder[trainNo+validNo:], :]

    return trainData, validData, testData, \
                trainTarget, validTarget, testTarget, dataOrder[0:trainNo]

def progressbar(percentage):
    bar_length=20
    hashes = '#' * int(percentage * bar_length)
    spaces = ' ' * (bar_length - len(hashes))
    sys.stdout.write("\rPercent: [%s] %f%%"%(hashes + spaces, percentage))
    sys.stdout.flush()


def relu(x):
    # Using T.nnet.relu gives me NaNs. No idea why.
    return T.switch(x > lib.floatX(0), x, lib.floatX(0))

def Conv2D(name, input_dim, output_dim, filter_size, inputs, mask_type=None, he_init=False):
    """
    inputs.shape: (batch size, height, width, input_dim)
    mask_type: None, 'a', 'b'
    output.shape: (batch size, height, width, output_dim)
    """
    def uniform(stdev, size):
        """uniform distribution with the given stdev and size"""
        return numpy.random.uniform(
            low=-stdev * numpy.sqrt(3),
            high=stdev * numpy.sqrt(3),
            size=size
        ).astype(theano.config.floatX)

    filters_init = uniform(
        1./numpy.sqrt(input_dim * filter_size * filter_size),
        # output dim, input dim, height, width
        (output_dim, input_dim, filter_size, filter_size)
    )

    if he_init:
        filters_init *= lib.floatX(numpy.sqrt(2.))

    if mask_type is not None:
        filters_init *= lib.floatX(numpy.sqrt(2.))

    filters = lib.param(
        name+'.Filters',
        filters_init
    )

    if mask_type is not None:
        mask = numpy.ones(
            (output_dim, input_dim, filter_size, filter_size), 
            dtype=theano.config.floatX
        )
        center = filter_size//2
        for i in range(filter_size):
            for j in range(filter_size):
                    if (j > center) or (j==center and i > center):
                        mask[:, :, j, i] = 0.
        for i in range(N_CHANNELS):
            for j in range(N_CHANNELS):
                if (mask_type=='a' and i >= j) or (mask_type=='b' and i > j):
                    mask[
                        j::N_CHANNELS,
                        i::N_CHANNELS,
                        center,
                        center
                    ] = 0.

        filters = filters * mask

    # conv2d takes inputs as (batch size, input channels, height, width)
    inputs = inputs.dimshuffle(0, 3, 1, 2)
    result = T.nnet.conv2d(inputs, filters, border_mode='half', filter_flip=False)

    biases = lib.param(
        name+'.Biases',
        numpy.zeros(output_dim, dtype=theano.config.floatX)
    )
    result = result + biases[None, :, None, None]

    return result.dimshuffle(0, 2, 3, 1)

def Conv1D(name, input_dim, output_dim, filter_size, inputs, apply_biases=True):
    """
    inputs.shape: (batch size, height, input_dim)
    output.shape: (batch size, height, output_dim)
    * performs valid convs
    """
    def uniform(stdev, size):
        """uniform distribution with the given stdev and size"""
        return numpy.random.uniform(
            low=-stdev * numpy.sqrt(3),
            high=stdev * numpy.sqrt(3),
            size=size
        ).astype(theano.config.floatX)

    filters = lib.param(
        name+'.Filters',
        uniform(
            1./numpy.sqrt(input_dim * filter_size),
            # output dim, input dim, height, width
            (output_dim, input_dim, filter_size, 1)
        )
    )

    # conv2d takes inputs as (batch size, input channels, height[?], width[?])
    inputs = inputs.reshape((inputs.shape[0], inputs.shape[1], 1, inputs.shape[2]))
    inputs = inputs.dimshuffle(0, 3, 1, 2)
    result = T.nnet.conv2d(inputs, filters, border_mode='valid', filter_flip=False)

    if apply_biases:
        biases = lib.param(
            name+'.Biases',
            numpy.zeros(output_dim, dtype=theano.config.floatX)
        )
        result = result + biases[None, :, None, None]

    result = result.dimshuffle(0, 2, 3, 1)
    return result.reshape((result.shape[0], result.shape[1], result.shape[3]))

def Skew(inputs):
    """
    input.shape: (batch size, HEIGHT, WIDTH, dim)
    """
    buffer = T.zeros(
        (inputs.shape[0], inputs.shape[1], 2*inputs.shape[2] - 1, inputs.shape[3]),
        theano.config.floatX
    )

    for i in range(HEIGHT):
        buffer = T.inc_subtensor(buffer[:, i, i:i+WIDTH, :], inputs[:,i,:,:])

    return buffer

def Unskew(padded):
    """
    input.shape: (batch size, HEIGHT, 2*WIDTH - 1, dim)
    """
    return T.stack([padded[:, i, i:i+WIDTH, :] for i in range(HEIGHT)], axis=1)
    
def binarize(images):
    """
    Stochastically binarize values in [0, 1] by treating them as p-values of
    a Bernoulli distribution.
    """
    return (numpy.random.uniform(size=images.shape) < images).astype('float32')

def DiagonalLSTM(name, input_dim, inputs):
    """
    inputs.shape: (batch size, height, width, input_dim)
    outputs.shape: (batch size, height, width, DIM)
    """
    inputs = Skew(inputs)

    input_to_state = Conv2D(name+'.InputToState', input_dim, DIM, 1, inputs, mask_type='None')

    batch_size = inputs.shape[0]

    c0_unbatched = lib.param(
        name + '.c0',
        numpy.zeros((HEIGHT, DIM), dtype=theano.config.floatX)
    )
    c0 = T.alloc(c0_unbatched, batch_size, HEIGHT, DIM)

    h0_unbatched = lib.param(
        name + '.h0',
        numpy.zeros((HEIGHT, DIM), dtype=theano.config.floatX)
    )
    h0 = T.alloc(h0_unbatched, batch_size, HEIGHT, DIM)

    def step_fn(current_input_to_state, prev_c, prev_h):
        # all args have shape (batch size, height, DIM)

        # TODO consider learning this padding
        prev_h = T.concatenate([
            T.zeros((batch_size, 1, DIM), theano.config.floatX), 
            prev_h
        ], axis=1)
        state_to_state = Conv1D(name+'.StateToState', DIM, 4*DIM, 2, prev_h, apply_biases=False)

        gates = current_input_to_state + state_to_state

        o_f_i = T.nnet.sigmoid(gates[:,:,:3*DIM])
        o = o_f_i[:,:,0*DIM:1*DIM]
        f = o_f_i[:,:,1*DIM:2*DIM]
        i = o_f_i[:,:,2*DIM:3*DIM]
        g = T.tanh(gates[:,:,3*DIM:4*DIM])

        new_c = (f * prev_c) + (i * g)
        new_h = o * T.tanh(new_c)

        return (new_c, new_h)

    outputs, _ = theano.scan(
        step_fn,
        sequences=input_to_state.dimshuffle(2,0,1,3),
        outputs_info=[c0, h0]
    )
    all_cs = outputs[0].dimshuffle(1,2,0,3)
    all_hs = outputs[1].dimshuffle(1,2,0,3)

    return Unskew(all_hs)

def DiagonalBiLSTM(name, input_dim, inputs):
    """
    inputs.shape: (batch size, height, width, input_dim)
    inputs.shape: (batch size, height, width, DIM)
    """
    # corner 1
    forward = DiagonalLSTM(name+'.Forward', input_dim, inputs)
    # corner 2
    backward = DiagonalLSTM(name+'.Backward', input_dim, inputs[:,:,::-1,:])[:,:,::-1,:]
    # corner 3, 4
    corner3 = DiagonalLSTM(name+'.corner3', input_dim, inputs[:,::-1,:,:])[:,::-1,:,:]
    corner4 = DiagonalLSTM(name+'.corner4', input_dim, inputs[:,::-1,::-1,:])[:,::-1,::-1,:]
    
    hiddenLayer = T.concatenate([
                    forward, backward, corner3, corner4
                        ], axis=3) # along the DIM direction. Now we have deepth*4
    return hiddenLayer

    # return forward + backward + corner3 +corner4
    

# build the structure
# inputs.shape: (batch size, height, width, channels)
data = T.tensor4('inputs')
targets = T.tensor4('targets')

output = Conv2D('InputConv', N_CHANNELS, DIM, 7, data, mask_type='None')

if MODEL=='pixel_rnn':

    output = DiagonalBiLSTM('LSTM1', DIM, output)
    output = Conv2D('OutputConv0', DIM*4, DIM, 1, output, mask_type='None', he_init=True)
    output = relu(output)
    output = DiagonalBiLSTM('LSTM2', DIM, output)

elif MODEL=='pixel_cnn':
    # The paper doesn't specify how many convs to use, so I picked 4 pretty
    # arbitrarily.
    for i in range(4):
        output = Conv2D('PixelCNNConv'+str(i), DIM, DIM, 3, output, mask_type='None', he_init=True)
        output = relu(output)

# DIM*4 to DIM, to DIM, to DIM,  to 1
output = Conv2D('OutputConv1', DIM*4, DIM, 1, output, mask_type='None', he_init=True)
output = relu(output)

output = Conv2D('OutputConv2', DIM, DIM, 1, output, mask_type='None', he_init=True)
output = relu(output)

# TODO: for color images, implement a 256-way softmax for each RGB channel here
# we don't need it....
output = Conv2D('OutputConv3', DIM, 1, 1, output, mask_type='None')

# Here should be softmax?
# The answer is NO. Softmax and sigmoid are similiar. 
# softmax will let the addition of probability to 1. So it use to classification.
output = T.nnet.sigmoid(output)

cost = T.mean(T.nnet.binary_crossentropy(output, targets))

params = lib.search(cost, lambda x: hasattr(x, 'param'))
lib.utils.print_params_info(params)

grads = T.grad(cost, wrt=params, disconnected_inputs='warn')
grads = [T.clip(g, lib.floatX(-GRAD_CLIP), lib.floatX(GRAD_CLIP)) for g in grads]

updates = lasagne.updates.adam(grads, params, learning_rate=1e-3)

train_fn = theano.function(
    inputs=[data,targets],
    outputs =[cost],
    updates=updates,
    on_unused_input='warn',
    allow_input_downcast=True
)

eval_fn = theano.function(
    inputs=[data,targets],
    outputs =[cost],
    on_unused_input='warn',
    allow_input_downcast=True
)

sample_fn = theano.function(
    inputs=[data,targets],
    outputs =[output],
    on_unused_input='ignore',
    allow_input_downcast=True
)



# main program
print ("Prepare data:")

IDList = list()
with open('IDs.txt', 'rb') as f:
    for line in f:
        IDList.append(line)


print ("Training!")
total_iters = 0
total_time = 0.
last_print_time = 0.
last_print_iters = 0

# for epoch in itertools.count():

    
costs = []
start_time = time.time()
    
trainData, validData, testData, \
    trainTarget, validTarget, testTarget, trainIndex = prepareData(IDList)

test = zip(testData, testTarget)
    
for epoch in range(STOP_ITERS):
    trainIndex = [i for i in range(len(trainIndex))]
    # important: shuffle inputs. cannot shuffle zip. 
    
    shuffle(trainIndex)
    trainData = trainData[trainIndex]
    trainTarget = trainTarget[trainIndex]
    train = zip(trainData, trainTarget)
    pairNo = 0
    for images, targets in train:
        # add a process bar at here
        progressbar((pairNo+1)/len(trainData))
        pairNo += 1
        # print (images.shape)
        images = images.reshape((BATCH_SIZE, HEIGHT, WIDTH, 1))
        targets = targets.reshape((BATCH_SIZE, HEIGHT, WIDTH, 1))
        # print (images.shape)
        
        cost = train_fn(images, targets)
        total_iters += 1
        # print (total_iters)
        # print (total_time)
        print (cost)
        costs.append(cost)
   # train all images, and then validation
    dev_costs = []
    if EVAL_DEV_COST:
        valid = zip(validData, validTarget)
        validDataNo = 0
        for images, targets in valid:
            progressbar((validDataNo+1)/len(validData))
            validDataNo += 1
            images = images.reshape((-1, HEIGHT, WIDTH, 1))
            targets = targets.reshape((-1, HEIGHT, WIDTH, 1))
            dev_cost = eval_fn(images, targets)
            print (dev_cost)
            dev_costs.append(dev_cost)
    else:
        dev_costs.append(0.)
    
    total_time = time.time() - start_time
    print ("epoch:{}\ttotal iters:{}\ttrain cost:{}\tdev cost:{}\ttotal time:{}\ttime per iter:{}".format(
            epoch,
            total_iters,
            numpy.mean(costs),
            numpy.mean(dev_costs),
            total_time,
            total_time / total_iters
         ))
    
# save about 10 images of validation
saveImage = validData[0:10]
saveTarget = validTarget[0:10]
saveData = zip(saveImage, saveTarget)
saveDataNo = 0
for images, targets in saveData:
    images = images.reshape((-1, HEIGHT, WIDTH, 1))
    targets = targets.reshape((-1, HEIGHT, WIDTH, 1))
    segmentation = sample_fn(images, targets)
    # segmentation as only one array (batch size is 1)in a list, so read it out.
    segmentation = segmentation[0]
    segmentation = segmentation.reshape((HEIGHT, WIDTH))
    images = images.reshape((HEIGHT, WIDTH))    
    # binary
    segmentationBI = binarize(segmentation)
        
    targets = targets.reshape((HEIGHT, WIDTH))
    logTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    tag = "epoch{}_No{}_time{}".format(epoch, saveDataNo, logTime)
    nameSeg = 'Segmentation_'+tag+'.png'
    nameGT = 'GroundTruth_'+tag+'.png'
    nameBI = 'BiS_'+tag+'.png'
    nameOrigin = 'ORI'+tag+'.png'
    mpimg.imsave(nameSeg, segmentation, cmap='Greys_r')
    mpimg.imsave(nameBI, segmentationBI, cmap='Greys_r')
    mpimg.imsave(nameGT, targets, cmap='Greys_r')
    mpimg.imsave(nameOrigin, images, cmap='Greys_r')
    saveDataNo += 1