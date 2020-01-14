import class_dodger
import pygame
import numpy
import math
import random
import os
import time

def distance_f(x1, y1, x2, y2):
   return math.sqrt(math.pow(x2 - x1, 2) + math.pow(y2 - y1, 2))

def dab_value(arr_list, coords, max_value, decay_rate = 0.66, mult_thresh = 0.10):
   def add_value(m_vect):
      if (0 <= curr_coords[0] < len(arr_list)) and  (0 <= curr_coords[1] < len(arr_list[0])):
         arr_list[curr_coords[0]][curr_coords[1]] += decay_value
      curr_coords[0] += m_vect[0]
      curr_coords[1] += m_vect[1]

   dist_to_mid = 1
   arr_list[coords[0]][coords[1]] += max_value
   decay_value = max_value * (1 - decay_rate)

   while (decay_value >= (max_value * mult_thresh)):
      curr_coords = [coords[0] - dist_to_mid, coords[1]]
      for diag_br in range(dist_to_mid):
         add_value((1, 1))
      for diag_bl in range(dist_to_mid):
         add_value((1, -1))
      for diag_ul in range(dist_to_mid):
         add_value((-1, -1))
      for diag_ur in range(dist_to_mid):
         add_value((-1, 1))

      decay_value *= (1 - decay_rate)
      dist_to_mid += 1

def can_bullet_hit_bot(screen, bullet, entity_bot, m_mode = 0, desired_away_dist = 10.0):
   valid_radius = (entity_bot.get_image_orig().get_width() + bullet.image.get_width()) / 2.0 + desired_away_dist

   bullet_arb_x, bullet_arb_y = bullet.center_float[0], bullet.center_float[1]
   bot_arb_x, bot_arb_y = entity_bot.rect.centerx, entity_bot.rect.centery
   dist_target = distance_f(bullet_arb_x, bullet_arb_y, bot_arb_x, bot_arb_y)
   m_vect = entity_bot.get_move_vector(m_mode)

   while (dist_target > valid_radius):
      bullet_arb_x += math.sin(bullet.get_direction() + math.pi / 2.0) * bullet.get_velocity()
      bullet_arb_y += math.cos(bullet.get_direction() + math.pi / 2.0) * bullet.get_velocity()
      bot_arb_x += m_vect[0]
      bot_arb_y += m_vect[1]

      image_radius = entity_bot.get_image_orig().get_width() / 2.0
      if (bot_arb_x < image_radius):
         bot_arb_x = image_radius
      if (bot_arb_x > screen.get_width() - image_radius):
         bot_arb_x = screen.get_width() - image_radius
      if (bot_arb_y > screen.get_height() - image_radius):
         bot_arb_y = screen.get_height() - image_radius
      if (bot_arb_y < image_radius):
         bot_arb_y = image_radius

      dist_target = distance_f(bullet_arb_x, bullet_arb_y, bot_arb_x, bot_arb_y)

      if not ((0 <= bullet_arb_x <= screen.get_width()) and (0 <= bullet_arb_y <= screen.get_height())):
         return False
   return True

def proc_entity_shoot(is_user, entity, screen):
   bullet_dir = entity.get_direction()
   bullet_coords = (entity.rect.centerx, entity.rect.centery)
   bullet = class_dodger.Bullet(screen, bullet_coords, is_user, bullet_dir)
   return bullet

def think_as_bot(danger_value, screen, bullet_sprites, entity_user, entity_bot, nodes = 9, update_value = 10.0):
   def add_wall_example():
      #side_walls for: Top, Bot, Left, Right
      side_walls = [(entity_bot.rect.centerx, 0), (entity_bot.rect.centerx, screen.get_height()), (0, entity_bot.rect.centery), (screen.get_width(), entity_bot.rect.centery)]
      bot_box_rad = entity_bot.get_box_side() // 2

      wall_field_infos = []
      for side_wall in side_walls:
         wall_coords = entity_bot.get_grid_box(side_wall[0], side_wall[1])
         if (wall_coords != (-1, -1)):
            wall_field_infos.append(wall_coords)

      if wall_field_infos:
         wall_field = numpy.zeros(shape = (entity_bot.get_box_side(), entity_bot.get_box_side()))
         walk_dirs = [m_move for m_move in range(1, 9)]

         while wall_field_infos:
            wall_coords = wall_field_infos.pop(0)
            dab_value(wall_field, wall_coords, update_value, decay_rate = 0.85)

         dir_removals = 0
         for index_move in range(bot_box_rad):
            if (wall_field[bot_box_rad - index_move][bot_box_rad] == update_value):
               walk_dirs.remove(1)
               dir_removals += 1
            if (wall_field[bot_box_rad][bot_box_rad + index_move] == update_value):
               walk_dirs.remove(3)
               dir_removals += 1
            if (wall_field[bot_box_rad + index_move][bot_box_rad] == update_value):
               walk_dirs.remove(5)
               dir_removals += 1
            if (wall_field[bot_box_rad][bot_box_rad - index_move] == update_value):
               walk_dirs.remove(7)
               dir_removals += 1
            if (dir_removals >= 2):
               for diag_value in [2, 4, 6, 8]:
                  neighbour_l = diag_value - 1
                  neighbour_r = (diag_value + 1) if (diag_value < 8) else 1
                  if (neighbour_l not in walk_dirs) and (neighbour_r not in walk_dirs) and (diag_value in walk_dirs):
                     walk_dirs.remove(diag_value)
                     break

         for walk_dir_index in walk_dirs:
            entity_bot.add_labeled_example(wall_field, walk_dir_index)

   # Bullet Field
   new_danger_value = 0
   if bullet_sprites and (not entity_bot.get_reboot_time()):
      bullet_field = numpy.zeros(shape = (entity_bot.get_box_side(), entity_bot.get_box_side()))
      for bullet_sprite in bullet_sprites:
         if can_bullet_hit_bot(screen, bullet_sprite, entity_bot) and bullet_sprite.get_is_from_user():
            bullet_coords = entity_bot.get_grid_box(bullet_sprite.rect.centerx, bullet_sprite.rect.centery)
            if (bullet_coords != (-1, -1)):
               dab_value(bullet_field, bullet_coords, update_value)
               #rewarded_index = entity_bot.predict_in_frame(bullet_field, walk = False)
               add_wall_example()

               for m_iter in range(1, 9):
                  if not can_bullet_hit_bot(screen, bullet_sprite, entity_bot, m_mode = m_iter):
                     entity_bot.add_labeled_example(bullet_field, m_iter)

      new_danger_value = bullet_field.sum()
      rewarded_index = entity_bot.predict_in_frame(bullet_field)#, walk = False)
      if (new_danger_value < danger_value):
         entity_bot.add_labeled_example(bullet_field, rewarded_index)

   return new_danger_value

def get_init_sprites(screen, box_side, side_length = 25):
   spawn_user = (screen.get_width() * 0.15, screen.get_height() * 0.5)
   spawn_bot = (screen.get_width() * 0.5, screen.get_height() * 0.5)

   entity_user = class_dodger.User(screen, spawn_user)
   entity_bot = class_dodger.Bot(screen, spawn_bot, box_side, side_length)
   gen_record_label = class_dodger.GenRecordLabel()

   return entity_bot, entity_user, gen_record_label

def main_display():
   screen = pygame.display.set_mode((1280, 960))
   pygame.display.set_caption("Dodger")
   pygame.display.set_icon(pygame.image.load("resources\\images\\image_icon.png").convert_alpha())
   return screen

def main_background(screen):
   background = pygame.Surface(screen.get_size())
   background.fill((250, 250, 250))
   screen.blit(background, (0, 0))
   return background

def draw_sprites_all(screen, entity_bot, entity_user, bullet_sprites, gen_record_label):
   background = main_background(screen)
   sprites_all = pygame.sprite.LayeredUpdates(bullet_sprites, entity_bot, entity_user, gen_record_label)
   sprites_all.clear(screen, background)
   sprites_all.update()
   sprites_all.draw(screen)

def handle_collisions(entity_user, entity_bot, bullet_sprites):
   pos_user = (entity_user.rect.centerx, entity_user.rect.centery)
   pos_bot = (entity_bot.rect.centerx, entity_bot.rect.centery)

   get_radius = True
   for bullet_sprite in bullet_sprites:
      if get_radius:
         valid_radius = (entity_user.get_image_orig().get_width() + bullet_sprite.image.get_width()) / 2.0
         get_radius = False
      pos_bullet = (bullet_sprite.rect.centerx, bullet_sprite.rect.centery)

      if bullet_sprite.get_is_from_user():
         if (distance_f(pos_bullet[0], pos_bullet[1], pos_bot[0], pos_bot[1]) <= valid_radius) \
            and not entity_bot.get_reboot_time():
            entity_bot.reboot()
            entity_bot.push_input()
            bullet_sprite.kill()
      else:
         if (distance_f(pos_bullet[0], pos_bullet[1], pos_user[0], pos_user[1]) <= valid_radius) \
            and not entity_user.get_reboot_time():
            entity_user.reboot()
            bullet_sprite.kill()

def handling_key_press(entity_user, entity_bot):
   for event in pygame.event.get():
      if event.type == pygame.QUIT:
         return False
      elif event.type == pygame.KEYDOWN:
         if event.key == pygame.K_ESCAPE:
            return False
         elif event.key == pygame.K_z:
            if not entity_user.get_reboot_time():
               entity_user.reboot()
         elif event.key == pygame.K_x:
            if not entity_bot.get_reboot_time():
               entity_bot.reboot()
   return True

def handling_mouse_hold(screen, entity_user, entity_bot):
   bullet_sprites = []
   if pygame.mouse.get_pressed()[0] and entity_user.can_use_gun():
      entity_user.set_gun_cooldown(entity_user.get_gun_fatigue())
      bullet_sprites.append(proc_entity_shoot(True, entity_user, screen))
      #bullet_sprites.append(proc_entity_shoot(False, entity_bot, screen))
   return bullet_sprites

def handling_input(danger_value, screen, entity_user, entity_bot, bullet_sprites, gen_record_label):
   cont_game_loop = handling_key_press(entity_user, entity_bot)
   new_bullet_sprites = handling_mouse_hold(screen, entity_user, entity_bot)
   if new_bullet_sprites:
      bullet_sprites.add(new_bullet_sprites)
   entity_bot.set_user_coords(entity_user.rect.center)
   danger_value = think_as_bot(danger_value, screen, bullet_sprites, entity_user, entity_bot)
   if (entity_bot.get_reboot_time() == 1):
      gen_record_label.set_gen_record(entity_bot.get_gen_record())

   return cont_game_loop, danger_value

def proc_game_loop(screen, game_loop = True):
   BOX_SIDE = 25
   SIDE_LENGTH = 81

   clock = pygame.time.Clock()
   entity_bot, entity_user, gen_record_label = get_init_sprites(screen, BOX_SIDE)
   bullet_sprites = pygame.sprite.OrderedUpdates()

   danger_value = -1
   while game_loop:
      clock.tick(60)
      game_loop, danger_value = handling_input( \
         danger_value, screen, entity_user, entity_bot, bullet_sprites, gen_record_label)
      handle_collisions(entity_user, entity_bot, bullet_sprites)
      draw_sprites_all(screen, entity_bot, entity_user, bullet_sprites, gen_record_label)
      pygame.display.flip()

def main():
   numpy.set_printoptions(threshold=numpy.inf)

   pygame.init()
   screen = main_display()
   proc_game_loop(screen)
   os._exit(1)

if __name__ == "__main__":
   main()