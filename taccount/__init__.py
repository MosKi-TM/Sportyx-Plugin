from pyplanet.apps.config import AppConfig
from .Tac import Tac
from pyplanet.apps.core.trackmania import callbacks as tm_signals
from pyplanet.apps.core.maniaplanet import callbacks as mp_signals
from pyplanet.contrib.command import Command
from .views import TotalTimeWidget, TotalList
import time

class TacConfig(AppConfig):
	app_dependencies = ['core.maniaplanet']

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.tac = Tac(self)
		self.widget = TotalTimeWidget(self)
		self.cooldown = 0
		self.whitelist = []
		self.dedimania_enabled = False


	async def on_start(self):
		await self.instance.command_manager.register(
			Command(command='tops', target=self.show_records_list)
		)
		self.context.signals.listen(mp_signals.map.map_end , self.map_start)
		self.context.signals.listen(mp_signals.player.player_connect, self.player_connect)
		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)
		await self.tac.on_start()
		await self.widget.Refresh_scores()
		self.tac.prev_map = self.tac.get_current_map()
		for player in self.instance.player_manager.online:
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)
			
	async def map_start(self, map, **kwargs):
		self.dedimania_enabled = ('dedimania' in self.instance.apps.apps and 'dedimania' not in self.instance.apps.unloaded_apps)
		self.widget.map_count += 1
		
		await TotalList(self).Refresh_scores()
		await self.widget.Refresh_scores()
		

		
		if self.instance.map_manager.next_map.name == self.tac.waitingmap:
			await self.unlock_server()

		if self.tac.get_current_map() == self.tac.waitingmap:
			await self.lock_server()

		for player in self.instance.player_manager.online:
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)
		
		message = "{} :current map, {} :waitingmap".format(self.tac.get_current_map(), self.tac.waitingmap)
		await self.instance.chat(message)
		self.tac.prev_map = self.tac.get_current_map()



		async def lock_server(self):
			self.whitelist = []
			
			for player in self.instance.player_manager.online:
				self.instance.gbx('AddGuest', player.login)
				self.whitelist.append(player.login)
			
			await self.load_guestlist()
			

		async def unlock_server(self):
			for player in self.whitelist:
				self.instance.gbx('RemoveGuest', player)

			self.whitelist = []

		async def load_guestlist(self):
			setting = settings.GUESTLIST_FILE
			if isinstance(setting, dict) and self.instance.process_name in setting:
				setting = setting[self.instance.process_name]
			if not isinstance(setting, str):
				setting = None

			file_name = setting.format(server_login=self.instance.game.server_player_login)
			try:
				await self.instance.player_manager.save_guestlist(filename=file_name)
			except:
				await self.instance.chat('$ff0Guestlist saving failed to {}'.format(file_name))

	async def refresh_widget(self, **kwargs):
		for player in self.instance.player_manager.online:
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)

	async def player_connect(self, player, is_spectator, source, signal):
		if self.tac.get_current_map() != self.tac.waitingmap:
			if player.level == 0:	
				if self.whitelist != []:
					if player.login not in self.whitelist:
						self.instance.gbx('Kick', player.login)
						
		TotalTimeWidget.get_player(str(player))
		await self.widget.display(player=player)
player=player)

	async def get_differences(abc, player, data = None, **kwargs):
	
		await  DifferenceList(self, data['login']).display(player=player.login)
		return 
		
		