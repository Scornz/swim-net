from swimnet import SwimNet

# Location of csv file containing all times and results
data = 'data/swimmers.csv'
net = SwimNet(data, epochs=60, use_diff=False, metric='Top 3 Power Points')
# Plot the distribution over a couple of events (show correlation of speed)
net.plot_loss()

net = SwimNet(data, epochs=60, use_diff=False, metric='Top 3 Ratio')
net.plot_loss()