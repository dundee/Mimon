#!/usr/bin/env python
#       Copyright 2009 Daniel Milde <info@milde.cz>
#       Based on load.sh originally created by Lars Kotthoff http://www.metalhead.ws/rrdtool


import re
import rrdtool
import time
from threading import Thread
import os.path

def create(data_dir):
	rrdtool.create(os.path.join(data_dir, 'cpu.rrd'),
	                             '--step', '60',
	                             'DS:load:GAUGE:180:0:U',
	                             'DS:user:COUNTER:180:0:U',
	                             'DS:nice:COUNTER:180:0:U',
	                             'DS:system:COUNTER:180:0:U', #heartbeat:min:max

	                             'RRA:AVERAGE:0.5:1:1440',   #instances
	                             'RRA:AVERAGE:0.5:1440:1',   #real avg
	                             'RRA:MIN:0.5:1440:1',
	                             'RRA:MAX:0.5:1440:1'   #xff:steps:rows
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
	path = os.path.join(data_dir, 'cpu.rrd')
	if not os.path.exists(path):
		create(data_dir)
	
	fp = open('/proc/loadavg')
	line = fp.readline()
	fp.close()

	load = re.sub('^[0-9\.]+ ([0-9\.]+) .+', '\\1', line).strip()

	fp = open('/proc/stat')
	line = fp.readline()
	fp.close()
	(user, nice, system) = re.sub('^cpu +([0-9]+) ([0-9]+) ([0-9]+).+', '\\1 \\2 \\3', line).strip().split(' ')

	values = ':'.join( (load, user, nice, system) )

	#print 'cpu '+values

	rrdtool.update(path,
	               'N:' + values
	)
	return values

def graph(data_dir, target_dir):
	png_path = os.path.join(target_dir, 'cpu.png')
	rrd_path = os.path.join(data_dir, 'cpu.rrd')
	rrdtool.graph(png_path,
	              '--imgformat', 'PNG',
	              '--alt-y-grid',
	              '--lower-limit', '0',
	              '--units-length', '5',
	              '--title', 'Load and CPU stats',
	              '--vertical-label', 'Load',
	              '--width', '700',
	              '--height', '300',
	              '--color', 'ARROW#000000',
	              '--x-grid', 'MINUTE:30:MINUTE:30:HOUR:1:0:%H',

	              'DEF:load='+rrd_path+':load:AVERAGE',
	              'DEF:user='+rrd_path+':user:AVERAGE',
	              'DEF:nice='+rrd_path+':nice:AVERAGE',
	              'DEF:sys='+rrd_path+':system:AVERAGE',

	              'CDEF:cpu=user,nice,sys,+,+',
	              'CDEF:reluser=load,user,100,/,*',
	              'CDEF:relnice=load,nice,100,/,*',
	              'CDEF:relsys=load,sys,100,/,*',
	              'CDEF:idle=load,100,cpu,-,100,/,*',

	              'HRULE:1#000000',

	              'AREA:reluser#FF0000:CPU user',
	              'AREA:relnice#00AAFF:CPU nice:STACK',
	              'AREA:relsys#FFFF00:CPU system:STACK',
	              'AREA:idle#00FF00:CPU idle:STACK',

	              'LINE2:load#000888:Load average 5 min',

	              'COMMENT:	\j',
	              'COMMENT:\j',
	              'COMMENT:	',

	              'GPRINT:cpu:MIN:CPU usage minimum\: %2.2lf%%',
	              'GPRINT:cpu:MAX:CPU usage maximum\: %2.2lf%%',
	              'GPRINT:cpu:AVERAGE:CPU usage average\: %2.2lf%%'
	)

"""
if __name__ == '__main__':
	#create()

	print update()
	print rrdtool.fetch('./memory.rrd', 'AVERAGE')

	#graph()
"""
