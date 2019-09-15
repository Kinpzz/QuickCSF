# -*- coding: utf-8 -*
'''Plot CSF curve'''

import logging
import argparse
from datetime import datetime
import math

import numpy

import matplotlib
import matplotlib.pyplot as plt
import pathlib
import argparseqt.gui
import argparseqt.groupingTools

from . import QuickCSF

def plotResults(results, plotFile=None, graph=None, responseHistory=None, showNumbers=True):
	''' plot and save the CSF curve
		Expects real-world value parameters
		The ploted CSF curve will be saved at plotFile
    '''
	if graph is None:
		fig = plt.figure()
		graph = fig.add_subplot(1, 1, 1)

		plt.ion()
		plt.show()

	frequencyDomain = QuickCSF.makeFrequencySpace(.005, 80, 50).reshape(-1,1)

	params = numpy.array([results['peakSensitivity'],
						 results['peakFrequency'],
						 results['bandwidth'],
			 			 results['delta']])
	data = QuickCSF.csf(params[0], params[1], params[2], params[3], frequencyDomain)
	data = numpy.power(10, data)
	line = graph.fill_between(
		frequencyDomain.reshape(-1),
		data.reshape(-1),
		color=(1, 0, 0, .5)
	)

	# plot response history
	if responseHistory is not None:
		## Chart responses
		positives = {'f':[], 's':[]}
		negatives = {'f':[], 's':[]}
		for record in responseHistory:
			stimValues = record[0]
			targetArray = positives if record[1] else negatives
			targetArray['f'].append(stimValues[1])
			targetArray['s'].append(1/stimValues[0])

		graph.plot(positives['f'], positives['s'], 'o', markersize=4, color=(.2, 1, .2))
		graph.plot(negatives['f'], negatives['s'], 'x', markersize=5, color=(1,0,0), markeredgewidth=2)

	graph.set_xlabel('Spatial frequency (CPD)')
	graph.set_xscale('log')
	graph.set_xlim((.25, 64))
	graph.set_xticks([1, 2, 4, 8, 16, 32])
	graph.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

	graph.set_ylabel('Sensitivity (1/contrast)')
	graph.set_yscale('log')
	graph.set_ylim((1, 400))
	graph.set_yticks([2, 10, 50, 200])
	graph.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

	graph.grid()

	if showNumbers:
		if data is not None:
			line.set_label(f'Aulcsf: %.2f' % (results['aulcsf']))
		graph.legend()

	graph.set_title(f'Contrast Sensitivity Function')

	if plotFile is not None:
		plt.savefig(plotFile)
	plt.ioff()
	plt.show()
	return graph

if __name__ == '__main__':
	parser = argparse.ArgumentParser()

	parser.add_argument('-sid', '--sessionID', default=None, help='A unique string to identify this observer/session')
	parser.add_argument('--plotPath', default='data/figures', help='If specified, path to save images')
	parser.add_argument('-s', '--peakSensitivity', type=float, default=100, help='Peak sensitivity (real-world value)')
	parser.add_argument('-f', '--peakFrequency', type=float, default=2.52, help='Peak frequency (real-world value)')
	parser.add_argument('-b', '--bandwidth', type=float, default=4, help='Bandwidth (real-world value)')
	parser.add_argument('-d', '--delta', type=float, default=35, help='Delta truncation (real-world value)')

	settings = argparseqt.groupingTools.parseIntoGroups(parser)
	if settings['sessionID'] is None: 
		from qtpy import QtWidgets
		from . import ui
		app = QtWidgets.QApplication()
		settings = ui.getSettings(parser, settings, ['sessionID'])
	results = {
		'peakSensitivity': settings['peakSensitivity'],
		'peakFrequency': settings['peakFrequency'],
		'bandwidth': settings['bandwidth'] ,
		'delta': settings['delta'],
	}
	if settings['plotPath'] is not None:	
		timeStamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
		plotPath = pathlib.Path(settings['plotPath'])
		if not plotPath.exists():
			plotPath.mkdir(parents=True)
		plotFile = plotPath / '{}-{}.png'.format(settings['sessionID'], timeStamp)
	else:
		plotFile = None
	plotResults(results=results, plotFile=plotFile, showNumbers=False)
