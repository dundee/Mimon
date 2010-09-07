#!/usr/bin/env python

import re
import rrdtool
import time
from threading import Thread
import os.path

def create(data_dir):
	rrdtool.create(os.path.join(data_dir, 'swap.rrd'),
	                             '--step', '60',
	                             'DS:used:GAUGE:180:0:U',
	                             'DS:free:GAUGE:180:0:U',
	                             'DS:total:GAUGE:180:0:U',

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
	path = os.path.join(data_dir, 'swap.rrd')
	if not os.path.exists(path):
		create(data_dir)
	
	fp = open('/proc/meminfo')
	lines = fp.readlines()
	fp.close()

	i = 0
	while not re.match('SwapTotal:', lines[i]):
		i += 1
	total   = int(re.sub('SwapTotal: +([0-9]+) kB', '\\1', lines[i])) / 1000
	free    = int(re.sub('SwapFree: +([0-9]+) kB', '\\1', lines[i+1])) / 1000

	used = total - free

	values = ':'.join( (str(used), str(free), str(total)) )

	#print 'swap '+values

	rrdtool.update(path,
	               'N:'+values
	)

def graph(data_dir, target_dir):
	png_path = os.path.join(target_dir, 'swap.png')
	rrd_path = os.path.join(data_dir, 'swap.rrd')
	rrdtool.graph(png_path,
	              '--imgformat', 'PNG',
	              '--title', 'Swap stats',
	              '--vertical-label', 'SWAP',
	              '--width', '600',
	              '--height', '400',
	              '--lower-limit', '0',

	              'DEF:used='+rrd_path+':used:AVERAGE',
	              'DEF:free='+rrd_path+':free:AVERAGE',
	              'DEF:total='+rrd_path+':total:AVERAGE',

	              'VDEF:usedavg=used,AVERAGE',
	              'VDEF:usedmax=used,MAXIMUM',
	              'VDEF:usedmin=used,MINIMUM',
	              'VDEF:freeavg=free,AVERAGE',
	              'VDEF:freemax=free,MAXIMUM',
	              'VDEF:freemin=free,MINIMUM',
	              'VDEF:totalavg=total,AVERAGE',
	              'VDEF:totalmax=total,MAXIMUM',
	              'VDEF:totalmin=total,MINIMUM',

	              'COMMENT:             Average   Maximum   Minimum\l',

	              'AREA:used#F00:Used   ',
	              'GPRINT:usedavg:%7.2lfM',
	              'GPRINT:usedmax:%7.2lfM',
	              'GPRINT:usedmin:%7.2lfM\l',
	              
	              'LINE2:total#000:Total  ',
	              'GPRINT:totalavg:%7.2lfM',
	              'GPRINT:totalmax:%7.2lfM',
	              'GPRINT:totalmin:%7.2lfM',
	)
