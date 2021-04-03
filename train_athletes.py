from swimnet import SwimNet

# Location of csv file containing all times and results
data = 'data/test_fake_data.csv'
net = SwimNet(data, epochs=30, use_diff=False)
# Plot the distribution over a couple of events (show correlation of speed)
net.plot_distribution('50 Free', '100 Fly', '200 Fly')
net.plot_loss()