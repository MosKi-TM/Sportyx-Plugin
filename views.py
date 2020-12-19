import math

from pyplanet.utils.style import style_strip
from pyplanet.utils.times import format_time
from pyplanet.views.generics.widget import TimesWidgetView
from pyplanet.views.generics.list import ManualListView
from pyplanet.utils import times
from .Tac import Tac
import mysql.connector
from pyplanet.conf import settings
global player_index
player_index = ''
global datas
datas = []

class TotalTimeWidget(TimesWidgetView):
	widget_x = -160
	widget_y = 70.5
	size_x = 38
	size_y = 55.5
	top_entries = 5
	title = 'Total Time'

	def __init__(self, app):
		super().__init__(app.context.ui)
		self.app = app
		self.id = 'pyplanet__widgets_tacount'
		self.instance = app.instance
		self.action = self.action_recordlist
		self.datas = []
		self.map_count = 1
		self.db_process = self.instance.process_name
		self.DB_NAME = settings.DATABASES[self.db_process]['NAME']
		self.DB_IP = settings.DATABASES[self.db_process]['OPTIONS']['host']
		self.DB_LOGIN = settings.DATABASES[self.db_process]['OPTIONS']['user']
		self.DB_PASSWORD = settings.DATABASES[self.db_process]['OPTIONS']['password']
		
	def get_player(player_args):
		global player_index
		player_index = player_args
		return
	
	async def Refresh_scores(self):
		db = mysql.connector.connect(
		  host=self.DB_IP,
		  user=self.DB_LOGIN,
		  passwd=self.DB_PASSWORD,
		  database=self.DB_NAME
		)
		map_attente = Tac.get_map(self)
		cursor = db.cursor()
		if map_attente:
			query = "SELECT login, nickname, SUM(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) AS total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id WHERE player.id IN (SELECT player_id FROM localrecord WHERE localrecord.map_id != "+str(map_attente)+") AND map.id !="+str(map_attente)+" GROUP BY nickname ORDER BY total ASC"
		else:
			query = "SELECT login, nickname, SUM(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) AS total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id WHERE player.id IN (SELECT player_id FROM localrecord) GROUP BY nickname ORDER BY total ASC"
		cursor.execute(query)
		self.datas = cursor.fetchall()

	async def get_context_data(self):
		self.widget_y = 12.5 if self.app.dedimania_enabled else 70.5
		self.title = "Total Time ({})".format(self.map_count)
		context = await super().get_context_data()
		
		
		index_range = 10
		data_length = 0
		datas_length = 0
		player_spot = 0
		toprange = 0
		
		
		global player_index		
		pindex_length = len(self.datas)
		try:
			pindex = [x[0] for x in self.datas].index(player_index)
		except:
			pindex = 0
		index = 1
		list_records = []
		min_index = 0
		max_index = 0
		if self.datas != 0:
			for login, nickname, total in self.datas[:5]:
				list_record = dict()
				list_record['index'] = index	
				list_record['color'] = '$ff0'				
				if login == player_index:
					list_record['color'] = '$0f3'
				list_record['nickname'] = nickname
				list_record['score'] = times.format_time(int(total))
				list_records.append(list_record)
				index += 1
			if pindex_length > 5:
				if pindex > 15 :
					min_index = pindex - 5
					max_index = pindex + 5
					index = pindex - 4
				else:
					min_index = 5
					max_index = 15
					
			for login, nickname, total in self.datas[min_index:max_index]:
				list_record = dict()
				list_record['index'] = index
				list_record['color'] = '$fff'
				if login == player_index:
					list_record['color'] = '$0f3'
				list_record['nickname'] = nickname
				list_record['score'] = times.format_time(int(total))
				list_records.append(list_record)
				index += 1

		context.update({
				'times': list_records
		})	
		
		return context
		
	async def action_recordlist(self, player, **kwargs):
		await self.app.show_records_list(player)
		
class TotalList(ManualListView):
	title = 'Total Time'
	icon_style = 'Icons128x128_1'
	icon_substyle = 'Total Time'
	
	fields = [
		{
			'name': '#',
			'index': 'index',
			'sorting': True,
			'searching': False,
			'width': 10,
			'type': 'label'
		},
		{
			'name': 'Player',
			'index': 'player_nickname',
			'sorting': False,
			'searching': True,
			'width': 70
		},
		{
			'name': 'Times',
			'index': 'score',
			'sorting': True,
			'searching': False,
			'width': 30,
			'type': 'label'
		},
		{
			'name': 'Difference',
			'index': 'difference',
			'sorting': True,
			'searching': False,
			'width': 50,
			'type': 'label'
		},
		{
			'name': 'Number of maps',
			'index': 'map_nb',
			'sorting': True,
			'searching': False,
			'width': 20,
			'type': 'label'
		},
	]
	
	def __init__(self, app, *args, **kwargs):
		super().__init__(self,*args, **kwargs)
		self.app = app
		self.manager = app.context.ui
		self.instance = app.instance
		self.db_process = self.instance.process_name
		self.datas = []
		self.cooldown = 0
		self.DB_NAME = settings.DATABASES[self.db_process]['NAME']
		self.DB_IP = settings.DATABASES[self.db_process]['OPTIONS']['host']
		self.DB_LOGIN = settings.DATABASES[self.db_process]['OPTIONS']['user']
		self.DB_PASSWORD = settings.DATABASES[self.db_process]['OPTIONS']['password']
		
	async def ms_time(self, time):
		if len(str(time)) == 0:
			return "000"
		elif len(str(time)) == 1:
			return "00%i" %(time)
		elif len(str(time)) == 2:
			return "0%i" %(time)
		else:
			return time
			
	async def tm_time(self, time):
		if len(str(time)) == 0:
			return "00"
		elif len(str(time)) == 1:
			return "0%i" %(time)
		else:
			return time
		
	async def Refresh_scores(self):
		global datas
		db_list = mysql.connector.connect(
		  host=self.DB_IP,
		  user=self.DB_LOGIN,
		  passwd=self.DB_PASSWORD,
		  database=self.DB_NAME
		)
		map_attente = Tac.get_map(self)
		cursor = db_list.cursor()
		if map_attente:
			query = "SELECT login, nickname, SUM(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) AS total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id WHERE player.id IN (SELECT player_id FROM localrecord WHERE localrecord.map_id != "+str(map_attente)+") AND map.id !="+str(map_attente)+" GROUP BY nickname ORDER BY total ASC"
		else:
			query = "SELECT login, nickname, SUM(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) AS total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id WHERE player.id IN (SELECT player_id FROM localrecord) GROUP BY nickname ORDER BY total ASC"
		cursor.execute(query)
		datas = cursor.fetchall()
		return

	async def get_data(self):
		global datas
		db2_list = mysql.connector.connect(
		  host=self.DB_IP,
		  user=self.DB_LOGIN,
		  passwd=self.DB_PASSWORD,
		  database=self.DB_NAME
		)
		db3_list = mysql.connector.connect(
		  host=self.DB_IP,
		  user=self.DB_LOGIN,
		  passwd=self.DB_PASSWORD,
		  database=self.DB_NAME
		)
		map_attente = Tac.get_map(self)
		index_range = 10
		data_length = 0
		datas_length = 0
		player_spot = 0
		toprange = 0

		index = 1
		items = []
		difference = ''
		
		for login, nickname, total in datas:
			cursor2 = db2_list.cursor()
			cursor3 = db3_list.cursor()
			player_index_query = 'SELECT id FROM `player` WHERE login=\'' + str(login) + '\''
			cursor3.execute(player_index_query)
			player_id = cursor3.fetchall()
			if map_attente:
				map_count_query = 'SELECT COUNT(*) FROM localrecord WHERE player_id=' + str(player_id[0][0]) + ' AND map_id != ' + str(map_attente)
			else:
				map_count_query = 'SELECT COUNT(*) FROM localrecord WHERE player_id=' + str(player_id[0][0])
			cursor2.execute(map_count_query)
			map_number = cursor2.fetchall()
			if total is None:
				break
			if index > 1:
				difference = '$f00 + ' + str(await Tac.convert_time(self,(int(total)) - int(datas[0][2])))
			items.append({
				'index': index, 'player_nickname': nickname,
				'score': await Tac.convert_time(self,total),
				'difference': difference,
				'map_nb': map_number[0][0],
				'login': login,
			})
			index += 1
		return items

		