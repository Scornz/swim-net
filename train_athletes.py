import tensorflow as tf

from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras import optimizers
from tensorflow.keras.layers.experimental import preprocessing

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
from swimnet import SwimNet

# Make sure the venv is all set up and running correctly
print(tf.__version__)
# Location of csv file containing all times and results
data = 'data/test_fake_data.csv'
net = SwimNet(data, epochs=15)
# Plot the distribution over a couple of events (show correlation of speed)
net.plot_distribution('50 Free', '100 Fly', '200 Fly')
net.plot_loss()
