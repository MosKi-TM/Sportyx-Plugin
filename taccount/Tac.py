from pyplanet.apps.contrib.admin.server import ServerAdmin
from pyplanet.apps.core.maniaplanet.callbacks.player import player_chat
from pyplanet.contrib.command import Command
import mysql.connector
from pyplanet.conf import settings


class Tac( ServerAdmin ):

	def __init__( self, app ):
		super().__init__( app ) 
		self.context = app.context
		self.instance = app.instance
		self.db_process = self.instance.process_name
		self.prev_map = ""
		self.waitingmap = ""
		self.waitingmap_id = -1
		self.DB_NAME = settings.DATABASES[self.db_process]['NAME']
		self.DB_IP = settings.DATABASES[self.db_process]['OPTIONS']['host']
		self.DB_LOGIN = settings.DATABASES[self.db_process]['OPTIONS']['user']
		self.DB_PASSWORD = settings.DATABASES[self.db_process]['OPTIONS']['password']
	
	def get_map(self):
		return self.app.tac.waitingmap_id 
	
	def get_current_map(self):
		return self.instance.map_manager.current_map.name
	
	async def on_start(self):
		await self.instance.permission_manager.register('locdel', 'delete all local record', app=self.app, min_level=2)
		await self.instance.permission_manager.register('waitingmap', 'set waiting map', app=self.app, min_level=2)
		await self.instance.command_manager.register(
			Command(command='omerde', target=self.get_top),
			Command(command='locdel', target=self.delete_locals, perms='tacount:locdel', admin=True),
			Command(command='waitingmap', target=self.waiting_map, perms='tacount:waitingmap', admin=True),
			Command(command='test', target=self.db_debug),
			)
			
		player_chat.register(self.on_chat)
		
	
	async def ms_time(self, time):
		if len(str(time)) == 0:
			return "000"
		elif len(str(time)) == 1:
			return "00%i" %(time)
		elif len(str(time)) == 2:
			return "0%i" %(time)
		else:
			return time
    
	async def waiting_map(self,player,data,**kwargs):
		map_name = self.instance.map_manager.current_map.name
		message = '{} has been set as waiting maps (not counted in total times)'.format(
		self.instance.map_manager.current_map.name
		)
		await self.instance.chat(message)
		inutile_db = mysql.connector.connect(
			host=self.DB_IP,
			user=self.DB_LOGIN,
			passwd=self.DB_PASSWORD,
			database=self.DB_NAME
		)	
		self.waitingmap = map_name
		query = 'SELECT id FROM map WHERE name = \'' + map_name + "\'"
		cursor3 = inutile_db.cursor()
		cursor3.execute(query)
		map_data = cursor3.fetchall()
		self.waitingmap_id = int(map_data[0][0])
		self.app.widget.map_count = 0
		await self.app.refresh_widget()
		return

	async def tm_time(self, time):
		if len(str(time)) == 0:
			return "00"
		elif len(str(time)) == 1:
			return "0%i" %(time)
		else:
			return time

	async def delete_locals(self,player,data,**kwargs):
		local_db = mysql.connector.connect(
			host=self.DB_IP,
			user=self.DB_LOGIN,
			passwd=self.DB_PASSWORD,
			database=self.DB_NAME
		)
		cursor_to_delete = local_db.cursor()
		cursor_to_delete.execute("TRUNCATE `localrecord`;")
		message = '$fffLocal Record has been deleted'
		await self.instance.chat(message)
	
	async def convert_time(self, ms):
		h = ms//3600000
		m = (ms-h*3600000)//60000
		s = (ms-h*3600000-m*60000)//1000
		ms = (ms-h*3600000-m*60000-s*1000)
		if h == 0:    
			t = "%s:%s.%s" %(m,await self.tm_time(s),await self.ms_time(ms))
		else:
			t = "%i:%s:%s.%s" %(h,m,await self.tm_time(s),await self.ms_time(ms))
		return t
		
	async def exec_func(self, player, data, **kwargs):
		await TotalTimeWidget.show_top(self, player, data)
		
	async def get_top(self, player, data, **kwargs):
		global map_attente
		db = mysql.connector.connect(
		  host=self.DB_IP,
		  user=self.DB_LOGIN,
		  passwd=self.DB_PASSWORD,
		  database=self.DB_NAME
		)
		index_range = 10
		data_length = 0
		datas_length = 0
		player_spot = 0
		toprange = 0
		cursor = db.cursor()
		if self.waitingmap_id != -1:
			query = "SELECT nickname, sum(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) as total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id WHERE map.id != " + str(self.waitingmap_id) + " GROUP BY nickname ORDER BY total ASC"
		else:
			query = "SELECT nickname, sum(COALESCE(score, (SELECT min(score) FROM localrecord AS lr2 WHERE lr2.map_id = map.id)*2)) as total FROM map JOIN player LEFT JOIN localrecord AS lr1 ON lr1.player_id = player.id AND lr1.map_id = map.id GROUP BY nickname ORDER BY total ASC"
		cursor.execute(query)
		datas = cursor.fetchall()
		message = '$f00{}'.format(datas[0][1])
		await self.instance.chat(message, player)
		for i in range(len(datas[0:5])):
			message = '$fff{}$z$s$0f3.$fff{}$z$s$0f3 total time: $fff{}'.format(
				i+1,datas[i][0], await self.convert_time(datas[i][1])
			)
			await self.instance.chat(message, player)
		try:
			index = [x[0] for x in datas].index(player.nickname)
			if index < 15:
				raise ValueError
			else:
				x = index - 5
				for nickname, total in datas[index-5:index+5]:
					x += 1
					message = '$fff{}$z$s$0f3.$fff{}$z$s$0f3 total time: $fff{}'.format(
						x, nickname, await self.convert_time(total)
					)
					await self.instance.chat(message, player)
		except ValueError:
			for i in range(len(datas[5:15])):
				message = '$fff{}$z$s$0f3.$fff{}$z$s$0f3 total time: $fff{}'.format(
					i+6, datas[i+5][0], await self.convert_time(datas[i+5][1])
				)
				await self.instance.chat(message, player)
		return
	async def db_debug(self,player,data,**kwargs):
		process = self.instance.process_name
		message = message = '{}  ||| $fff{}'.format(
				self.waitingmap,
				self.get_current_map()
			)
		await self.instance.chat(message, player)