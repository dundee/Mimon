#!/usr/bin/env python

import re
import rrdtool
import time
from threading import Thread
import os.path

def create(data_dir):
	rrdtool.create(os.path.join(data_dir, 'memory.rrd'),
	                             '--step', '60',
	                             'DS:used:GAUGE:180:0:U',
	                             'DS:cached:GAUGE:180:0:U',
	                             'DS:buffers:GAUGE:180:0:U',
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
	path = os.path.join(data_dir, 'memory.rrd')
	if not os.path.exists(path):
		create(data_dir)
	
	fp = open('/proc/meminfo')
	lines = fp.readlines()
	fp.close()

	total   = int(re.sub('MemTotal: +([0-9]+) kB', '\\1', lines[0])) / 1000
	free    = int(re.sub('MemFree: +([0-9]+) kB', '\\1', lines[1])) / 1000
	buffers = int(re.sub('Buffers: +([0-9]+) kB', '\\1', lines[2])) / 1000
	cached  = int(re.sub('Cached: +([0-9]+) kB', '\\1', lines[3])) / 1000

	used = total - free - buffers - cached

	values = ':'.join( (str(used), str(cached), str(buffers), str(free), str(total)) )

	#print 'memory '+values

	rrdtool.update(path,
	               'N:'+values
	)

def graph(data_dir, target_dir):
	png_path = os.path.join(target_dir, 'memory.png')
	rrd_path = os.path.join(data_dir, 'memory.rrd')
	rrdtool.graph(png_path,
	              '--imgformat', 'PNG',
	              '--title', 'Memory stats',
	              '--vertical-label', 'RAM',
	              '--width', '600',
	              '--height', '400',
	              '--lower-limit', '0',

	              'DEF:used='+rrd_path+':used:AVERAGE',
	              'DEF:cached='+rrd_path+':cached:AVERAGE',
	              'DEF:buffers='+rrd_path+':buffers:AVERAGE',
	              'DEF:free='+rrd_path+':free:AVERAGE',
	              'DEF:total='+rrd_path+':total:AVERAGE',

	              'VDEF:usedavg=used,AVERAGE',
	              'VDEF:usedmax=used,MAXIMUM',
	              'VDEF:usedmin=used,MINIMUM',
	              'VDEF:cachedavg=cached,AVERAGE',
	              'VDEF:cachedmax=cached,MAXIMUM',
	              'VDEF:cachedmin=cached,MINIMUM',
	              'VDEF:buffersavg=buffers,AVERAGE',
	              'VDEF:buffersmax=buffers,MAXIMUM',
	              'VDEF:buffersmin=buffers,MINIMUM',
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

	              'AREA:cached#00F:Cached :STACK',
	              'GPRINT:cachedavg:%7.2lfM',
	              'GPRINT:cachedmax:%7.2lfM',
	              'GPRINT:cachedmin:%7.2lfM\l',

	              'AREA:buffers#0F0:Buffers:STACK',
	              'GPRINT:buffersavg:%7.2lfM',
	              'GPRINT:buffersmax:%7.2lfM',
	              'GPRINT:buffersmin:%7.2lfM\l',

	              'AREA:free#555:Free   :STACK',
	              'GPRINT:freeavg:%7.2lfM',
	              'GPRINT:freemax:%7.2lfM',
	              'GPRINT:freemin:%7.2lfM\l',

	              'LINE2:total#000:Total  ',
	              'GPRINT:totalavg:%7.2lfM',
	              'GPRINT:totalmax:%7.2lfM',
	              'GPRINT:totalmin:%7.2lfM',
	)
