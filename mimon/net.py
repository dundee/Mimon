#!/usr/bin/env python
#       Copyright 2009 Daniel Milde <info@milde.cz>
#       Based on load.sh originally created by Lars Kotthoff http://www.metalhead.ws/rrdtool


import re
import rrdtool
import time
from threading import Thread
import os.path

def create(data_dir):
	rrdtool.create(os.path.join(data_dir, 'net.rrd'),
	                             '--step', '60',
	                             'DS:download:COUNTER:180:0:U',
	                             'DS:upload:COUNTER:180:0:U',

	                             'RRA:AVERAGE:0.5:5:1440',
	                             'RRA:MAX:0.5:1440:1'
	)

class MyThread(Thread):
	def __init__(self):
		Thread.__init__(self)
		self.data_dir = '/var/lib/python-support/python2.6/mimon'
	def run(self):
		self.update_loop()
	def update_loop(self):
		while True:
			update(self.data_dir)
			time.sleep(60)

def update(data_dir):
	path = os.path.join(data_dir, 'net.rrd')
	if not os.path.exists(path):
		create(data_dir)
	
	fp = open('/proc/net/dev')
	lines = fp.readlines()
	fp.close()

	for line in lines:
		if re.search('eth0', line):
			eth = line
			break

	(interface, values) = eth.split(':')
	values = values.split()

	download = values[0]
	upload   = values[8]

	values = ':'.join( (download, upload) )

	#print 'net '+values

	rrdtool.update(path,
	               'N:' + values
	)

def graph(data_dir, target_dir):
	png_path = os.path.join(target_dir, 'net.png')
	rrd_path = os.path.join(data_dir, 'net.rrd')
	rrdtool.graph(png_path,
	              '--imgformat', 'PNG',
	              '--title', 'Network stats',
	              '--vertical-label', 'bytes/sec',
	              '--width', '600',
	              '--height', '400',
	              '--lower-limit', '0',

	              'DEF:download='+rrd_path+':download:AVERAGE',
	              'DEF:upload='+rrd_path+':upload:AVERAGE',

	              'LINE:download#0F0:Download',
	              'GPRINT:download:MAX:Max download\: %2.2lf bytes/sec',

	              'LINE:upload#00F:Upload',
	              'GPRINT:upload:MAX:Max upload\: %2.2lf bytes/sec',
	)
