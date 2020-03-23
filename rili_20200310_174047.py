# -*- coding: utf-8 -*-

#生成isweekwork.cfg和isholiday.cfg

from pyquery import PyQuery as pq
import datetime

year = 2020 #datetime.datetime.now().year

#周末补班
#fo = open("isweekwork.cfg", "w")
#节假日
fo = open("isholiday.cfg", "w")

for m in "01,02,03,04,05,06,07,08,09,10,11,12".split(','):

	rl_url = 'https://wannianrili.51240.com/ajax/?q=%s-%s&v=18121801' % (year, m)
	print(rl_url)
	html = pq(url=rl_url)

	#周末补班
	#xiu = html('a.wnrl_riqi_ban')
	#节假日
	xiu = html('a.wnrl_riqi_xiu')

	#print(xiu)

	for i in xiu.children('.wnrl_td_gl').text().split(' '):
		if i != '':
			day = '%s-%s-%s\n' % (year, m, i)
			fo.write(day)
			print(day)
fo.close()