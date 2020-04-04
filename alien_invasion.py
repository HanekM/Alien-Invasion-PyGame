import pygame
from pygame.sprite import Group

from settings import Settings
from game_stats import GameStats
from scorebord import Scorebord
from button import Button
from ship import Ship
from alien import Alien
import game_functions as gf

def run_game():
	
	# Инициализация игры и создание обьекта екрана
	pygame.init()
	ai_settings = Settings()
	screen = pygame.display.set_mode((ai_settings.screen_width, 
	ai_settings.screen_height))
	pygame.display.set_caption('Alien Invasion')
	# Создание екземпляра для хранения игровой статистики, Scorebord
	# и кнопки Плей
	stats = GameStats(ai_settings)
	sb = Scorebord(ai_settings, screen, stats)
	play_button = Button(ai_settings, screen, 'Play')
	#Создание корабля, груп для пуль, пришельцeв
	ship = Ship(ai_settings, screen)
	bullets = Group()
	aliens = Group()
	gf.create_fleet(ai_settings, screen, ship, aliens)
	
	# Запуск основного цикла игры
	while True:
		
		# Отслеживание событий нажатия мыши\клавиш
		gf.check_events(ai_settings, screen, stats, sb, play_button, ship, 
		aliens, bullets)
		ship.update()
		gf.update_bullets(ai_settings, screen, stats, sb, ship, aliens, 
		bullets)
		if stats.game_active:
			gf.update_aliens(ai_settings, stats, screen, sb, ship, aliens, 
			bullets)	
		gf.update_screen(ai_settings, screen, stats, sb, ship, aliens,
		bullets, play_button)
		
run_game()








