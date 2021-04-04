from swimnet import SwimNet

# Location of csv file containing all times and results
data = 'data/swimmers.csv'
net = SwimNet(data, epochs=5, use_diff=False, metric='Top 3 Power Points')
# Plot the distribution over a couple of events (show correlation of speed)
net.plot_distribution('50 FR', '1650 FR', '200 FL')
net.plot_distribution('100 BR', '100 FL', '200 IM')
net.plot_loss()