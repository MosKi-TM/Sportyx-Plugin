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
		
		for player in self.instance.player_manager.online:
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)
		self.tac.prev_map = self.tac.get_current_map()


	async def refresh_widget(self, **kwargs):
		for player in self.instance.player_manager.online:
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)

	async def player_connect(self, player, is_spectator, source, signal):
			TotalTimeWidget.get_player(str(player))
			await self.widget.display(player=player)
	
	async def show_records_list(self, player, data = None, **kwargs):
		
		now = int(round(time.time() * 1000))
		if now > self.cooldown:
			await TotalList(self).Refresh_scores()
			self.cooldown = now + 20000
		await TotalList(self).display(player=player.login)
		return
	
		
	async def get_differences(abc, player, data = None, **kwargs):
	
		await  DifferenceList(self, data['login']).display(player=player.login)
		return 
		
		