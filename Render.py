from abc import ABCMeta, abstractmethod
import pygame
import math

SQRT3 = math.sqrt( 3 )

class Render( pygame.Surface ):

	__metaclass__ = ABCMeta

	def __init__( self, map, radius=16 ):
		self.map = map
		self.radius = radius

		# Colors for the map
		self.GRID_COLOR = pygame.Color( 50, 50, 50 )

		super( Render, self ).__init__( ( self.width, self.height ) )
		pass


	@property
	def width( self ):
		return	math.ceil( self.map.cols / 2.0 ) * 2 * self.radius + \
				math.floor( self.map.cols / 2.0 ) * self.radius + 1
	@property
	def height( self ):
		return ( self.map.rows + .5 ) * self.radius * SQRT3 + 1

	def get_surface( self, ( row, col ) ):
		"""
		Returns a subsurface corresponding to the surface, hopefully with trim_cell wrapped around the blit method.
		"""
		width = 2 * self.radius
		height = self.radius * SQRT3

		top = ( row - math.ceil( col / 2.0 ) ) * height + ( height / 2 if col % 2 == 1 else 0 )
		left = 1.5 * self.radius * col

		return self.subsurface( pygame.Rect( left, top, width, height ) )

	# Draw methods
	@abstractmethod
	def draw( self ):
		"""
		An abstract base method for various render objects to call to paint 
		themselves.  If called via super, it fills the screen with the colorkey,
		if the colorkey is not set, it sets the colorkey to magenta (#FF00FF)
		and fills this surface. 
		"""
		color = self.get_colorkey()
		if not color:
			magenta = pygame.Color( 255, 0, 255 )
			self.set_colorkey( magenta )
			color = magenta
		self.fill( color )

	# Identify cell
	def get_cell( self, ( x, y ) ):
		"""
		Identify the cell clicked in terms of row and column
		"""
		# Identify the square grid the click is in.
		row = math.floor( y / ( SQRT3 * self.radius ) )
		col = math.floor( x / ( 1.5 * self.radius ) )

		# Determine if cell outside cell centered in this grid.
		x = x - col * 1.5 * self.radius
		y = y - row * SQRT3 * self.radius

		# Transform row to match our hex coordinates, approximately
		row = row + math.floor( ( col + 1 ) / 2.0 )

		# Correct row and col for boundaries of a hex grid 
		if col % 2 == 0:
			if 	y < SQRT3 * self.radius / 2 and x < .5 * self.radius and \
				y < SQRT3 * self.radius / 2 - x:
				row, col = row - 1, col - 1
			elif y > SQRT3 * self.radius / 2 and x < .5 * self.radius and \
				y > SQRT3 * self.radius / 2 + x:
				row, col = row, col - 1
		else:
			if 	x < .5 * self.radius and abs( y - SQRT3 * self.radius / 2 ) < SQRT3 * self.radius / 2 - x:
				row, col = row - 1 , col - 1
			elif y < SQRT3 * self.radius / 2:
				row, col = row - 1, col


		return ( row, col ) if self.map.valid_cell( ( row, col ) ) else None

class RenderUnits( Render ):
	"""
	A premade render object that will automatically draw the Units from the map 
	
	"""
	def draw( self ):
		"""
		Calls unit.paint for all units on self.map
		"""
		super( RenderUnits, self ).draw()
		units = self.map.positions

		for position, unit in units.items():
			surface = self.get_surface( position )
			unit.paint( surface )

class RenderGrid( Render ):
	def draw( self ):
		"""
		Draws a hex grid, based on the map object, onto this Surface
		"""
		super( RenderGrid, self ).draw()
		# A point list describing a single cell, based on the radius of each hex
		cell = [	( .5 * self.radius, 0 ),
					( 1.5 * self.radius, 0 ),
					( 2 * self.radius, SQRT3 / 2 * self.radius ),
					( 1.5 * self.radius, SQRT3 * self.radius ),
					( .5 * self.radius, SQRT3 * self.radius ),
					( 0, SQRT3 / 2 * self.radius )
		]
		for col in range( self.map.cols ):
			# Alternate the offset of the cells based on column
			offset = self.radius * SQRT3 / 2 if col % 2 else 0
			for row in range( self.map.rows ):
				# Calculate the offset of the cell
				top = offset + SQRT3 * row * self.radius
				left = 1.5 * col * self.radius
				# Create a point list containing the offset cell
				points = [( x + left, y + top ) for ( x, y ) in cell]
				# Draw the polygon onto the surface
				pygame.draw.polygon( self, self.GRID_COLOR, points, 1 )


if __name__ == '__main__':
	from Map import Map, MapUnit
	import sys

	class Unit( MapUnit ):
		color = pygame.Color( 200, 200, 200 )
		def paint( self, surface ):
			radius = surface.get_width() / 2
			pygame.draw.circle( surface, self.color, ( radius, int( SQRT3 / 2 * radius ) ), int( radius - radius * .3 ) )

	m = Map( ( 5, 5 ) )
	m.positions[( 0, 0 ) ] = Unit( m )
	m.positions[( 3, 2 ) ] = Unit( m )
	m.positions[( 5, 3 ) ] = Unit( m )
	m.positions[( 5, 4 ) ] = Unit( m )
	print( m.ascii() )

	grid = RenderGrid( m, radius=32 )
	units = RenderUnits( m, radius=32 )

	try:
		pygame.init()
		fpsClock = pygame.time.Clock()

		window = pygame.display.set_mode( ( 640, 480 ), 1 )
		from pygame.locals import QUIT, MOUSEBUTTONDOWN

		#Leave it running until exit
		while True:
			for event in pygame.event.get():
				if event.type == QUIT:
					pygame.quit()
					sys.exit()
				if event.type == MOUSEBUTTONDOWN:
					print( units.get_cell( event.pos ) )

			grid.draw()
			units.draw()
			window.blit( grid, ( 0, 0 ) )
			window.blit( units, ( 0, 0 ) )
			pygame.display.update()
			fpsClock.tick( 10 )
	finally:
		pygame.quit()





