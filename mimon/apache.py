#!/usr/bin/env python
#       Copyright 2009 Daniel Milde <info@milde.cz>
#       Based on load.sh originally created by Lars Kotthoff http://www.metalhead.ws/rrdtool


import re
import rrdtool
import time
from threading import Thread
import os.path
import urllib2
import sys

def create(data_dir):
	rrdtool.create(os.path.join(data_dir, 'apache.rrd'),
	                             '--step', '60',
	                             'DS:requests:GAUGE:180:0:U',
	                             'DS:bytes:GAUGE:180:0:U',
	                             'DS:busy:GAUGE:180:0:U',
	                             'DS:idle:GAUGE:180:0:U',
	                             'DS:load:GAUGE:180:0:U',

	                             'RRA:AVERAGE:0.5:1:2016', #points
	                             'RRA:AVERAGE:0.5:2016:1', #real avg
	                             'RRA:MAX:0.5:2016:1',
	                             'RRA:MIN:0.5:2016:1'
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
	path = os.path.join(data_dir, 'apache.rrd')
	if not os.path.exists(path):
		create(data_dir)
	try:
		fp = urllib2.urlopen('http://localhost/server-status?auto')
		if fp.code != 200:
			return
	except urllib2.HTTPError, e:
		return
	
	lines = fp.readlines()
	fp.close()
	
	lines = dict( [ line.split(':') for line in lines ] )
	requests = bytes = busy = idle = load = 0
	
	if lines.has_key('ReqPerSec'): requests = float(lines['ReqPerSec']);
	if lines.has_key('BytesPerSec'): bytes    = float(lines['BytesPerSec'])
	if lines.has_key('BusyWorkers'): busy     = int(lines['BusyWorkers'])
	if lines.has_key('IdleWorkers'): idle     = int(lines['IdleWorkers'])
	if lines.has_key('CPULoad'): load     = float(lines['CPULoad'])
	
	values = ':'.join( map(str, (requests, bytes, busy, idle, load)) )

	#print 'apache '+values

	rrdtool.update(path,
	               'N:' + values
	)

def graph(data_dir, target_dir):
	png_path = os.path.join(target_dir, 'apache.png')
	rrd_path = os.path.join(data_dir, 'apache.rrd')
	rrdtool.graph(png_path,
	              '--imgformat', 'PNG',
	              '--title', 'Apache stats',
	              '--vertical-label', 'requests/sec',
	              '--width', '600',
	              '--height', '400',
	              '--lower-limit', '0',

	              'DEF:requests='+rrd_path+':requests:AVERAGE',

	              'LINE:requests#0F0:Requests',
	              'GPRINT:requests:MAX:Max requests\: %2.2lf requests/sec',
	)

