# import pygame and math modules
import pygame
import math

#import datetime to convert stored time to readable version
import datetime

# import some color-related modules
import matplotlib.colors as mc
import colorsys

#import logging to do logging-related stuff
import logging


# initialise the pygame modules
pygame.init()


# define window properties
width, height = 800, 800

#define a window and a surface
window = pygame.display.set_mode((width, height))
surface = pygame.Surface((width*2, height*2))
#set a window title
pygame.display.set_caption('Planet Simulation')

#set a font
font = pygame.font.SysFont('comicsans', 16)

#set a basicconfig for logging
logging.basicConfig(level=logging.DEBUG, filename=f'logs/{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.log', filemode='w',
					format='%(asctime)s - %(levelname)s - %(message)s')


# define a colors class
class colors:
	white = (255, 255, 255)
	yellow = (255, 255, 0)
	blue = (100, 149, 237)
	red = (188, 39, 50)
	dark_grey = (80, 78, 81)

#define a functions class
class functions:
	def adjust_lightness(input_color, amount):
		color = (input_color[0]/255, input_color[1]/255, input_color[2]/255)
		try:
			c = mc.cnames[color]
		except:
			c = color
		c = colorsys.rgb_to_hls(*mc.to_rgb(c))
		float_color = colorsys.hls_to_rgb(
			c[0], max(0, min(1, amount / 255 * c[1])), c[2])
		return list(round(i*255) for i in float_color)
	def is_close(num1, num2, factor):
		if abs(num1[0]-num2[0]) <= factor and abs(num1[1]-num2[1]) <= factor:
			return True
		else:
			return False

# define a Planet class
class Planet:
	AU = 149.6e6 * 1000
	G = 6.67428e-11
	scale = 225 / AU  # 1AU = x pixels where x is the number next to / AU
	current_time = 0
	timestep = 3600*6  # 6 hours
	display_step = 3600*6#3600*24*7  # 7 days

	def __init__(self, name, x, y, radius, color, mass):
		self.name = name
		self.x = x
		self.y = y
		self.radius = radius
		self.color = color
		self.mass = mass

		self.orbit = []
		self.is_sun = False
		self.distance_to_sun = 0
		self.last_circle = None

		self.x_vel = 0
		self.y_vel = 0

	def draw(self, win, surf):
		x = self.x * self.scale + width / 2
		y = self.y * self.scale + height / 2

		if len(self.orbit) > 2:
			updated_points = []
			for point in self.orbit:
				x, y = point
				x = x * self.scale + width / 2
				y = y * self.scale + height / 2
				updated_points.append((x, y))

			# draw each one of the last 255 lines inputed on the list a bit darker
			for hue, coords in enumerate(updated_points[-255:-1]):
				pygame.draw.line(surf, functions.adjust_lightness(
					self.color, hue), coords, updated_points[-255:][hue+1])

		self.last_circle = pygame.draw.circle(surf, self.color, (x, y), self.radius*self.scale)

		if not self.is_sun:
			distance_text = font.render(
				f"{round(self.distance_to_sun/1000)} km", 1, colors.white)
			surf.blit(distance_text, (x, y + distance_text.get_height()/2))
	
		win.blit(surf, (0, 0))

	def attraction(self, other):
		# get distance to "other"
		other_x, other_y = other.x, other.y
		distance_x = other_x - self.x
		distance_y = other_y - self.y
		distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

		# if other is the Sun, save it
		if other.is_sun:
			self.distance_to_sun = distance

		# calculate the force
		force = self.G * self.mass * other.mass / distance**2
		# caculate the theta angle
		theta = math.atan2(distance_y, distance_x)
		force_x = math.cos(theta) * force
		force_y = math.sin(theta) * force
		return force_x, force_y

	def update_position(self, planets, insert_to_orbit=False):
		total_fx = total_fy = 0
		for planet in planets:
			if self == planet:
				continue

			fx, fy = self.attraction(planet)
			total_fx += fx
			total_fy += fy

		self.x_vel += total_fx / self.mass * self.timestep
		self.y_vel += total_fy / self.mass * self.timestep

		self.x += self.x_vel * self.timestep
		self.y += self.y_vel * self.timestep
		if insert_to_orbit:
			self.orbit.append((self.x, self.y))

			time_text = font.render(
				f"{datetime.timedelta(seconds=self.current_time)}", 1, colors.white)
			surface.blit(time_text, (width-time_text.get_width()-15, 5))

#function executed on startup
def main():
	logging.debug('Running program...\n')
	run = True
	#define a clock so that the game runs at a set amount of FPS
	clock = pygame.time.Clock()

	#define variables

	#define the planets
	sun = Planet('Sun', 0, 0, 695508 * 1000, colors.yellow, 1.98892 * 10**30)
	sun.is_sun = True

	earth = Planet('Earth', -1 * Planet.AU,  0, 6371 * 1000, colors.blue, 5.9742 * 10**24)
	earth.y_vel = 29.783 * 1000

	mars = Planet('Mars', -1.524 * Planet.AU, 0, 3390 * 1000, colors.red, 6.39 * 10**23)
	mars.y_vel = 24.077 * 1000

	mercury = Planet('Mercury', 0.387 * Planet.AU, 0, 2440 * 1000, colors.dark_grey, 3.30 * 10**23)
	mercury.y_vel = 47.4 * 1000

	venus = Planet('Venus', 0.723 * Planet.AU, 0, 6052 * 1000, colors.white, 4.8685 * 10**24)
	venus.y_vel = -35.02 * 1000

	planets = [sun, earth, mars, mercury, venus]

	while run:
		#define some variables
		global surface

		# run at 60fps
		clock.tick(60)
		surface.fill((0, 0, 0))
		window.blit(surface, (0, 0))

		#save queued events in a variable
		current_events = pygame.event.get()

		#check if should change mouse icon back to normal
		if not pygame.MOUSEMOTION in list(i.type for i in current_events):
			pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

		#hand queued events
		for event in current_events:
			#if X button is clicked, close
			if event.type == pygame.QUIT:
				run = False
			#if mid mouse button was scrolled, zoom in/out
			elif event.type == pygame.MOUSEWHEEL:
				logging.debug(f"Scroll: {event.y}")

				#scale the planets
				for planet in planets:
					planet.scale *= 1+event.y/10

			#if mouse was moved...
			elif event.type == pygame.MOUSEMOTION:
				#check if right button is being holded down
				if pygame.mouse.get_pressed(num_buttons=3)[0]:
					#if yes, do necessary actions to move the "solar system"

					#define some variables
					mouse_x, mouse_y = event.rel

					logging.debug(f'Mouse X: {mouse_x}, Mouse Y: {mouse_y}')

					#change each planet's position
					for planet in planets:
						planet.x += mouse_x / planet.scale
						planet.y += mouse_y / planet.scale

						#change cursor icon
						pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_SIZEALL)
						#update planet orbit (only the last 255 items to save time and resources)
						if len(planet.orbit) < 255:
							for index, pos in enumerate(planet.orbit[-len(planet.orbit):]):
								planet.orbit[-len(planet.orbit)+index] = [pos[0] + mouse_x / planet.scale, pos[1] + mouse_y / planet.scale]
						else:
							for index, pos in enumerate(planet.orbit[-255:]):
								planet.orbit[-255+index] = [pos[0] + mouse_x / planet.scale, pos[1] + mouse_y / planet.scale]

			elif event.type == pygame.MOUSEBUTTONDOWN:
				#check if mouse clicked wasn't a scroll button
				if not event.button in [1,2,3]:
					continue
				#check if mouse click is near to a planet in planets list:
				for planet in planets:
					#check if mouse was clicked within 10 pixels of a planet
					if functions.is_close(event.pos, planet.last_circle.center, 10):
						#if yes...
						logging.debug(f'Mouse click collides with planet "{planet.name}"')
						#center to that planet
						
						#begin by saving the current planet coords (because they will change)
						current_coords = [planet.x, planet.y]
						for second_planet in planets:
							second_planet.x -= current_coords[0]
							second_planet.y -= current_coords[1]
						
							#update each planet's orbit
							if len(second_planet.orbit) < 255:
								for index, pos in enumerate(second_planet.orbit[-len(second_planet.orbit):]):
									second_planet.orbit[-len(second_planet.orbit)+index] = [pos[0] - current_coords[0], pos[1] - current_coords[1]]
							else:
								for index, pos in enumerate(second_planet.orbit[-255:]):
									second_planet.orbit[-255+index] = [pos[0] - current_coords[0], pos[1] - current_coords[1]]
					
						#break the loop
						break

				#else, change mouse icon to normal
				else:
					pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)


		#loop through each planet
		for planet in planets:
			# update each planet's position a set amount of times BUT don't draw it
			for i in range(planet.display_step//planet.timestep):
				planet.update_position(planets)
				planet.current_time += planet.timestep

			#when done, update again and draw the planet
			planet.update_position(planets, insert_to_orbit=True)
			planet.current_time += planet.timestep

			planet.draw(window, surface)

		#update the display
		pygame.display.update()

	#when loop is interrupted, close the program
	logging.debug('Closing program...\n')

	pygame.quit()


if __name__ == "__main__":
	try:
		main()
	#if an Exception a raisen, log it
	except Exception as e:
		logging.exception('An exception has occured', exc_info=True)