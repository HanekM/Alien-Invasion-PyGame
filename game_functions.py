import sys
from time import sleep 

import pygame
from bullet import Bullet
from alien import Alien

def get_number_rows(ai_settings, ship_height, alien_height):
    """Determine the number of aliens that fit in the screen"""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (2 * alien_height))
    return number_rows
	

def get_number_aliens_x(ai_settings, alien_width):
	'''Вычисляет количество пришельцев в ряду'''
	available_space_x = ai_settings.screen_width - 2 * alien_width
	number_aliens_x = int(available_space_x / (2 * alien_width))
	return number_aliens_x
	
	
def create_alien(ai_settings, screen, aliens, alien_number, row_number):    
    """Create an alien and place it in the row"""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)
	

def create_fleet(ai_settings, screen, ship, aliens):
    """Create a full fleet of aliens"""
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_row =  get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    #Create the fleet of aliens.
    for row_number in range(number_row):
        for alien_number in range(number_aliens_x):
            create_alien(ai_settings, screen, aliens, alien_number, row_number)
	
	
def check_aliens_bottom(ai_settings, stats, screen, sb, ship, aliens, bullets):
	'''Проверяет, добрались ли пришельци до нижнего края екрана'''
	screen_rect = screen.get_rect()
	for alien in aliens.sprites():
		if alien.rect.bottom >= screen_rect.bottom:
			# Происходит то же, что и при столкновении с кораблем
			ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
			break
		
	
def update_aliens(ai_settings, screen, stats, sb, ship, aliens, bullets):	
	'''
	Проверяет, достиг ли флот края екрана, после чего
	обновляет позиции всех пришельцев во флоте
	'''
	check_fleet_edges(ai_settings, aliens)
	aliens.update()
	# Проверка коллизии 'пришелец-корабль'
	if pygame.sprite.spritecollideany(ship, aliens):
		ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
		# Проверка пришельцев, добравшихся до нижнего края экрана.
	check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, 
	bullets)
	

def check_fleet_edges(ai_settings, aliens):
	'''Реагирует на достижение пришельцем края екрана '''
	for alien in aliens.sprites():
		if alien.check_edges():
			change_fleet_direction(ai_settings, aliens)
			break

			
def change_fleet_direction(ai_settings, aliens):
	'''Опускает флот и меняет направление'''
	for alien in aliens.sprites():
		alien.rect.y += ai_settings.fleet_drop_speed
	ai_settings.fleet_direction *= -1
	
	
def check_keydown_events(event, ai_settings, screen, ship, bullets):
	'''Реагирует на нажатие клавиш'''
	if event.key == pygame.K_RIGHT:
		ship.moving_right = True
	elif event.key == pygame.K_LEFT:
		ship.moving_left = True	
	elif event.key == pygame.K_SPACE:
		#Создание новой пули и включение ее в групу bullets 
		new_bullet = Bullet(ai_settings, screen, ship)
		bullets.add(new_bullet)
	elif event.key == pygame.K_q:
		sys.exit()
		
		
def check_keyup_events(event, ship):
	'''Реагирует на отпускание клавиш'''
	if event.key == pygame.K_RIGHT:
		ship.moving_right = False
	elif event.type == pygame.KEYUP:
		ship.moving_left = False
			
	
def check_events(ai_settings, screen, stats, sb, play_button, ship, 
aliens, bullets):
	'''нажатие клавиш и мыши'''
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sys.exit()
		elif event.type == pygame.KEYDOWN:
			if len(bullets) < ai_settings.bullet_allowed:
				check_keydown_events(event, ai_settings, screen, ship, bullets)
		elif event.type == pygame.KEYUP:
			check_keyup_events(event, ship)
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mouse_x, mouse_y = pygame.mouse.get_pos()
			check_play_button(ai_settings, screen, stats, sb, play_button,
			ship, aliens, bullets, mouse_x, mouse_y)
	
			
def check_play_button(ai_settings, screen, stats, sb, play_button,
ship, aliens, bullets, mouse_x, mouse_y):
	'''Запускает игру при нажатии клавиши Плей'''
	button_clicked = play_button.rect.collidepoint(mouse_x, mouse_y)
	if button_clicked and not stats.game_active:
		# Сброс игровых настроек
		ai_settings.initialize_dynamic_settings()
		# Указатель мыши скрывается 
		pygame.mouse.set_visible(False)
		#Сброс игровой статистики
		stats.reset_stats()
		stats.game_active = True
		# Сброс изображения счетов и уровня
		sb.prep_score()
		sb.prep_high_score()
		sb.prep_level()
		sb.prep_ships()
		# Очистка списков пришельцев и пуль
		aliens.empty()
		bullets.empty()
		# Создание нового флота и размещение корабля в центре
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
		
def check_high_score(stats, sb):
	'''Проверяет, появился ли новый рекорд'''
	if stats.score > stats.high_score:
		stats.high_score = stats.score
		sb.prep_high_score()
		
			
			
def update_screen(ai_settings, screen, stats, sb, ship, aliens, 
bullets, play_button):
	
	'''Обновляет изображения на экране и отображает новый экран'''
	# При каждом проходе цикла перерисовывается экран.
	screen.fill(ai_settings.bg_color)
	
	#Все пули выводятся позади изображений корабля и пришельцев
	for bullet in bullets.sprites():
		bullet.draw_bullet()
	ship.blitme()
	aliens.draw(screen)
	# Отображение последнего прорисованого екрана		
	pygame.display.flip()
	# Вывод счета
	sb.show_score()
	# Кнопка Плей отображается в том случаетБ, если игра неактивна
	if not stats.game_active:
		play_button.draw_button()
		pygame.display.flip()
	


def update_bullets(ai_settings, screen, stats, sb, ship, 
aliens, bullets):
	'''Обновляет позиции пуль и удаляет старые'''
	#Обновление позиций пуль.
	bullets.update()
	#Удаление пуль, вышедших за екран
	for bullet in bullets.copy():
		if bullet.rect.bottom <= 0:
			bullets.remove(bullet)
	# Проверка попадания в пришельцев 
	# При обнаружении попадания удалить пулю и пришельца
	check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship,
	aliens, bullets)
	
def check_bullet_alien_collisions(ai_settings, screen, stats, sb, 
ship, aliens, bullets): 
	'''Проверка коллизии пуль с пришельцами'''
	collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
	if collisions:
		for aliens in collisions.values():
			stats.score += ai_settings.alien_points
			sb.prep_score()
			check_high_score(stats, sb)
	if len(aliens) == 0:
		# Уничтожение существующих пуль, создание нового флота и 
		# повышения скорости игры
		bullets.empty()
		ai_settings.increase_speed()
		#Увеличение уровня
		stats.level += 1
		sb.prep_level()
		create_fleet(ai_settings, screen, ship, aliens)
	
def ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets):
	'''Обрабатывает столкновение корабля с пришельцем'''
	if stats.ships_left > 0:
		# Уменьшение ships_left
		stats.ships_left -= 1
		#Обновление игровой информации
		sb.prep_ships()
		# Очистка списков пришельцев и пуль
		aliens.empty()
		bullets.empty()
		# Создание нового флота и размещение корабля в центре
		create_fleet(ai_settings, screen, ship, aliens)
		ship.center_ship()
		#Пауза
		sleep(0.5)
	else:
		stats.game_active = False
		pygame.mouse.set_visible(True)
		
	
			
	
	
	
	
	
	
	
	
	
	
		
