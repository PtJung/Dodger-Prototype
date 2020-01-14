import pygame
import math
import numpy
import random
import tensorflow as tf
from tensorflow import keras


class GenRecordLabel(pygame.sprite.Sprite):
    def __init__(self, init_gen_record = 1):
        pygame.sprite.Sprite.__init__(self)
        self.__gen_text_font = pygame.font.SysFont("Consolas", 14, bold = True)
        self.set_gen_record(init_gen_record)

    def set_gen_record(self, gen_record):
        self.__gen_record = gen_record
        self.update_image()

    def update_image(self, text_color = (20, 60, 60)):
        self.image = self.__gen_text_font.render("Gen: %d" % (self.__gen_record), 0, text_color)
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (5, 20)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, screen, init_coords, is_from_user, direction, velocity = 25):
        pygame.sprite.Sprite.__init__(self)

        self.__screen = screen
        self.__is_from_user = is_from_user
        self.__direction = direction
        self.__velocity = float(velocity)
        self.center_float = [init_coords[0], init_coords[1]]
        self.__init_bullet_image(init_coords[0], init_coords[1])

    def __init_bullet_image(self, init_coord_x, init_coord_y):
        self.image = pygame.image.load("resources\\images\\image_bullet.png").convert()
        self.image.set_colorkey((255, 255, 255))

        self.rect = self.image.get_rect()
        self.rect.centerx = init_coord_x
        self.rect.centery = init_coord_y

    def get_velocity(self):
        return self.__velocity

    def get_direction(self):
        return self.__direction

    def get_is_from_user(self):
        return self.__is_from_user

    def is_bullet_out_of_bounds(self):
        return (self.rect.bottom < -self.image.get_height() or \
                self.rect.top > self.__screen.get_height() + self.image.get_height()) or \
               (self.rect.right < -self.image.get_width() or \
                self.rect.left > self.__screen.get_width() + self.image.get_width())

    def update(self):
        bullet_direction = self.__direction + math.pi / 2.0
        self.center_float[0] += math.sin(bullet_direction) * self.__velocity
        self.center_float[1] += math.cos(bullet_direction) * self.__velocity
        self.rect.center = self.center_float

        if self.is_bullet_out_of_bounds():
            self.kill()

class Entity(pygame.sprite.Sprite):
    def __init__(self, screen, is_user, init_coords, move_speed = 8.0, gun_fatigue = 15, reboot_fatigue = 15):
        pygame.sprite.Sprite.__init__(self)

        self.__is_user = is_user
        self.__is_alive = True
        self.__screen = screen
        self.__move_speed = move_speed
        self.__init_coords = init_coords
        self.__direction = math.pi / 2.0
        self.__gun_fatigue = gun_fatigue
        self.__gun_cooldown = 0
        self.__reboot_time = 0
        self.__reboot_fatigue = reboot_fatigue

        self.__init_entity_image(self.__is_user, self.__init_coords[0], self.__init_coords[1])
        self.__image_orig = self.image

    def __init_entity_image(self, is_user, init_coord_x, init_coord_y):
        if is_user:
            self.image = pygame.image.load("resources\\images\\image_entity_user.png").convert()
        else:
            self.image = pygame.image.load("resources\\images\\image_entity_bot.png").convert()
        self.image.set_colorkey((255, 255, 255))

        self.rect = self.image.get_rect()
        self.rect.centerx = init_coord_x
        self.rect.centery = init_coord_y

    def get_move_vector(self, m_mode):
        m_vect = [0, 0]
        if (m_mode):
            if (m_mode in [6, 7, 8]):
                m_vect[0] -= self.__move_speed
            if (m_mode in [2, 3, 4]):
                m_vect[0] += self.__move_speed
            if (m_mode in [1, 2, 8]):
                m_vect[1] -= self.__move_speed
            if (m_mode in [4, 5, 6]):
                m_vect[1] += self.__move_speed
            if (m_mode in [2, 4, 6, 8]):
                m_vect[0] *= math.sqrt(2) / 2.0
                m_vect[1] *= math.sqrt(2) / 2.0

        return m_vect

    def move_in_direction(self, m_left, m_right, m_up, m_down):
        move_speed = self.__move_speed

        # Apply Pythagorean's theorem to diagonal movements
        if (m_left ^ m_right and m_up ^ m_down):
            move_speed *= math.sqrt(2) / 2.0

        # Move in the directions as indicated by the boolean parameters (+ vector)
        if (m_left):
            self.rect.centerx -= move_speed
        if (m_right):
            self.rect.centerx += move_speed
        if (m_up):
            self.rect.centery -= move_speed
        if (m_down):
            self.rect.centery += move_speed

        # Restrict movements to fit in the screen
        image_radius = self.__image_orig.get_width() / 2.0
        if (self.rect.centerx < image_radius):
            self.rect.centerx = image_radius
        if (self.rect.centerx > self.__screen.get_width() - image_radius):
            self.rect.centerx = self.__screen.get_width() - image_radius
        if (self.rect.centery > self.__screen.get_height() - image_radius):
            self.rect.centery = self.__screen.get_height() - image_radius
        if (self.rect.centery < image_radius):
            self.rect.centery = image_radius

    def move_step_to_center(self):
        def distance_f(x1, y1, x2, y2):
            return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        dists_to_center = []

        center = self.get_init_coords()
        arb_x, arb_y = self.rect.center

        for dir_unit_x in [-1, 0, 1]:
            for dir_unit_y in [-1, 0, 1]:
                move_speed = self.__move_speed
                if (dir_unit_x != 0 and dir_unit_y != 0):
                    move_speed *= math.sqrt(2) / 2.0

                new_arb_x = arb_x + dir_unit_x * move_speed
                new_arb_y = arb_y + dir_unit_y * move_speed

                dist_to_center = distance_f(center[0], center[1], new_arb_x, new_arb_y)
                dists_to_center.append((dist_to_center, new_arb_x, new_arb_y))

        min_dist_index = dists_to_center.index(min(dists_to_center))
        self.rect.centerx = dists_to_center[min_dist_index][1]
        self.rect.centery = dists_to_center[min_dist_index][2]

    def reboot(self):
        self.__gun_cooldown = 1
        self.__direction = math.pi / 2.0
        self.set_reboot_time(self.get_reboot_fatigue())
        self.__init_entity_image(self.__is_user, self.__init_coords[0], self.__init_coords[1])
        self.image = pygame.image.load("resources\\images\\image_entity_reboot.png").convert_alpha()

    def can_use_gun(self):
        return (self.get_gun_cooldown() == 0)

    def update_gun_cooldown(self):
        if (self.get_gun_cooldown() - 1) >= 0:
            self.set_gun_cooldown(self.get_gun_cooldown() - 1)

    def update_reboot_time(self):
        if (self.get_reboot_time() - 1) >= 0:
            self.set_reboot_time(self.get_reboot_time() - 1)

    def check_reboot_time(self):
        if (self.get_reboot_time() == 0):
            self.image = self.get_image_orig()

    def get_direction(self):
        return self.__direction

    def get_reboot_time(self):
        return self.__reboot_time

    def get_reboot_fatigue(self):
        return self.__reboot_fatigue

    def get_gun_cooldown(self):
        return self.__gun_cooldown

    def get_gun_fatigue(self):
        return self.__gun_fatigue

    def get_init_coords(self):
        return self.__init_coords

    def get_image_orig(self):
        return self.__image_orig

    def set_reboot_time(self, reboot_time):
        self.__reboot_time = reboot_time

    def set_reboot_fatigue(self, reboot_fatigue):
        self.__reboot_fatigue = reboot_fatigue

    def set_direction(self, direction):
        self.__direction = direction

    def set_gun_fatigue(self, gun_fatigue):
        self.__gun_fatigue = gun_fatigue

    def set_gun_cooldown(self, gun_cooldown):
        self.__gun_cooldown = gun_cooldown


class User(Entity):
    def __init__(self, screen, init_coords):
        Entity.__init__(self, screen, True, init_coords)
        self.__screen = screen

    def __face_cursor(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        vector = (float(mouseX - self.rect.centerx), float(mouseY - self.rect.centery))
        self.set_direction(-math.atan2(vector[1], vector[0]))
        angle_to_cursor = math.degrees(self.get_direction() - math.pi / 2.0)

        self.image = pygame.transform.rotate(self.get_image_orig(), angle_to_cursor)
        self.rect = self.image.get_rect(center = self.rect.center)
        self.image.get_rect(center = self.rect.center)

    def __move_controlled(self):
        m_left, m_right, m_up, m_down = False, False, False, False
        keyInput = pygame.key.get_pressed()

        if keyInput[pygame.K_LEFT] or keyInput[pygame.K_a]:
            m_left = True
        if keyInput[pygame.K_RIGHT] or keyInput[pygame.K_d]:
            m_right = True
        if keyInput[pygame.K_UP] or keyInput[pygame.K_w]:
            m_up = True
        if keyInput[pygame.K_DOWN] or keyInput[pygame.K_s]:
            m_down = True

        self.move_in_direction(m_left, m_right, m_up, m_down)

    def update(self):
        if not self.get_reboot_time():
            self.__face_cursor()
            self.__move_controlled()
            self.update_gun_cooldown()
        else:
            self.update_reboot_time()
            self.check_reboot_time()

class Bot(Entity):
    def __init__(self, screen, init_coords, box_side, side_length, nodes = 9):
        Entity.__init__(self, screen, False, init_coords)
        self.__list_features = []
        self.__list_labels = []
        self.__gen_record = 1
        self.__box_side = box_side
        self.__side_length = side_length
        self.__nodes = nodes
        self.__predict_cooldown = 0

        self.__dodge_model = keras.Sequential()
        self.__dodge_model.add(keras.layers.Flatten(input_shape = (box_side, box_side)))
        self.__dodge_model.add(keras.layers.Dense(360, activation = tf.nn.relu))
        self.__dodge_model.add(keras.layers.Dense(nodes, activation = tf.nn.softmax))
        self.__dodge_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    def __move_automatic(self, m_mode):
        m_left, m_right, m_up, m_down = False, False, False, False

        if (m_mode in [1, 2, 8]):
            m_up = True
        if (m_mode in [2, 3, 4]):
            m_right = True
        if (m_mode in [4, 5, 6]):
            m_down = True
        if (m_mode in [6, 7, 8]):
            m_left = True

        #print("move_automatic(): m_mode: (%d) %s %s %s %s" % (m_mode, str(m_left), str(m_right), str(m_up), str(m_down)))
        self.move_in_direction(m_left, m_right, m_up, m_down)

    def __face_user(self):
        vector = (float(self.__user_coords[0] - self.rect.centerx), float(self.__user_coords[1] - self.rect.centery))
        self.set_direction(-math.atan2(vector[1], vector[0]))
        angle_to_cursor = math.degrees(self.get_direction() - math.pi / 2.0)

        self.image = pygame.transform.rotate(self.get_image_orig(), angle_to_cursor)
        self.rect = self.image.get_rect(center = self.rect.center)
        self.image.get_rect(center = self.rect.center)

    def predict_in_frame(self, bullet_field, walk = True, predict_fatigue = 8):
        if (not self.__predict_cooldown):
            predict_out = self.__dodge_model.predict( \
                bullet_field.reshape((1, self.__box_side, self.__box_side))).tolist()[0]
            self.__predict_max = predict_out.index(max(predict_out[1:]))
            self.__predict_cooldown = predict_fatigue
        if walk:
            self.__move_automatic(self.__predict_max)
        return self.__predict_max

    def push_input(self, fit_epochs = 3):
        if (self.__list_features and self.__list_labels):
            input_features = numpy.array(self.__list_features)
            input_labels = numpy.array(self.__list_labels)

            self.__dodge_model.fit(input_features, input_labels, fit_epochs)
            self.__list_features, self.__list_labels = [], []
            self.__gen_record += 1

    def add_labeled_example(self, feature, label):
        self.__list_features.append(feature)
        self.__list_labels.append(label)

    def get_grid_box(self, entity_x, entity_y):
        relative_x = entity_x - self.rect.centerx
        relative_y = entity_y - self.rect.centery

        if not (self.__box_side % 2):
            self.__box_side += 1
        box_col = self.__box_side // 2
        box_row = box_col

        expandable_point = [0, 0]
        halved_side = self.__side_length // 2
        if relative_x:
            if (relative_x > halved_side):
                expandable_point[0] = halved_side
                while (relative_x >= expandable_point[0]):
                    expandable_point[0] += self.__side_length
                    box_col += 1
            elif (relative_x < -halved_side):
                expandable_point[0] = halved_side
                while (relative_x <= -expandable_point[0]):
                    expandable_point[0] += self.__side_length
                    box_col -= 1
        if relative_y:
            if (relative_y > halved_side):
                expandable_point[1] = halved_side
                while (relative_y >= expandable_point[1]):
                    expandable_point[1] += self.__side_length
                    box_row += 1
            elif (relative_y < -halved_side):
                expandable_point[1] = halved_side
                while (relative_y <= -expandable_point[1]):
                    expandable_point[1] += self.__side_length
                    box_row -= 1
        if not (0 <= box_row <= (self.__box_side - 1) and 0 <= box_col <= (self.__box_side - 1)):
            box_col, box_row = -1, -1

        return (box_row, box_col)

    def get_box_side(self):
        return self.__box_side

    def get_side_length(self):
        return self.__side_length

    def get_nodes(self):
        return self.__nodes

    def get_gen_record(self):
        return self.__gen_record

    def set_user_coords(self, user_coords):
        self.__user_coords = user_coords

    def update_predict_cooldown(self):
        if (self.__predict_cooldown > 0):
            self.__predict_cooldown -= 1

    def update(self):
        if not self.get_reboot_time():
            self.__face_user()
            self.update_predict_cooldown()
        else:
            self.update_reboot_time()
            self.check_reboot_time()