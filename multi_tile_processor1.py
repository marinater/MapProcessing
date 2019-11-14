from tile_processor import Graph
import os
import cv2
import numpy as np
import random

filetype = 'jpg'
source = './roads'
tile_size = (512, 512)

start_x, start_y = (7779, 12517)
end_x, end_y = (7781, 12520)

def stitchTiles():
	total_size = (end_y - start_y + 1) * tile_size[0], (end_x - start_x + 1) * tile_size[1], 3
	out = np.zeros( total_size, dtype=np.uint8)

	for x in range(end_x - start_x + 1):
		if x > 0:
			out[ :, x * tile_size[1], 2 ] = 255
	
		for y in range(end_y - start_y + 1):
			filename = '{}/{}_{}.{}'.format(source,x + start_x,y + start_y,filetype)
			y_range = tile_size[0] * y, tile_size[0] * y + tile_size[0]
			x_range = tile_size[1] * x, tile_size[1] * x + tile_size[1]

			out[ slice(*y_range), slice(*x_range), 0] = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
			if y > 0:
				out[ y * tile_size[0], :, 2 ] = 255
		

	cv2.imwrite('stitched.png', out)

def graph2img(graph):
	graph = graph.boundary_graph
	min_y = min(graph.values(), key=lambda v: v.position[0] ).position[0]
	min_x = min(graph.values(), key=lambda v: v.position[1] ).position[1]
	max_y = max(graph.values(), key=lambda v: v.position[0] ).position[0]
	max_x = max(graph.values(), key=lambda v: v.position[1] ).position[1]

	out = np.zeros( (max_y - min_y + 1, max_x - min_x + 1), dtype=np.uint8)

	for node in graph.values():
		pt1 = node.position
		out[pt1] = 255
	out = cv2.dilate(out, np.ones((10,10)))


	for node in graph.values():
		pt1 = node.position
		node_color = random.randint(0,255)

		for connected_node in node.connected:
			# if pt1[0] % 512 > 500 or pt1[0] % 512 < 10 or pt1[1] % 512 > 500 or pt1[1] % 512 < 10:
			pt2 = graph[connected_node].position
			out = cv2.line(out, pt1[::-1], pt2[::-1], node_color, 1, 8)

	disp = cv2.applyColorMap(out, cv2.COLORMAP_HSV)
	disp[out == 0, 2] = 0
	cv2.imwrite('out.png', disp)

def map2new(old, new):
	return { new[i] : old[i] for i in range(min(len(new),len(old))) }

def replaceNodes(tile, leading_edge, new_edge):
	conversion_map = map2new(leading_edge, new_edge)

	# Replace all instances of the old with the new
	for old_val, new_val in conversion_map.items():
		for key in tile.boundary_graph.keys():
			for key_index in range(len(tile.boundary_graph[key].connected )):
				if tile.boundary_graph[key].connected[key_index] == old_val:
					tile.boundary_graph[key].connected[key_index] = new_val

		tile.boundary_graph[new_val] = tile.boundary_graph.pop(old_val)

def mergeGraphs(combined, new):
	for key, val in new.boundary_graph.items():
		if key in combined.boundary_graph.items():
			combined.boundary_graph[key].connected.extend( new.boundary_graph[key].connected )
		else:
			combined.boundary_graph[key] = new.boundary_graph[key]






combined_graph = Graph()

for x in range(start_x, end_x + 1):
	combined_col_graph = Graph()

	for y in range(start_y, end_y + 1):
		# Load new tile
		filename = '{}/{}_{}.{}'.format(source,x,y,filetype)
		tile_id = (x, y)
		pos_offset = ((y - start_y) * tile_size[0] , (x - start_x) * tile_size[1])

		new_tile = Graph(tile_id, pos_offset, filename)
		north_edge = new_tile.boundaries['north']

		# Figure out new to old mapping
		replaceNodes(new_tile, combined_col_graph.boundaries['south'], north_edge)
		# Merge new and old graphs
		mergeGraphs(combined_col_graph, new_tile)

		combined_col_graph.boundaries['south'] = new_tile.boundaries['south']


		combined_col_graph.boundaries['west'].extend(new_tile.boundaries['west'])
		combined_col_graph.boundaries['east'].extend(new_tile.boundaries['east'])

	replaceNodes(combined_col_graph, combined_graph.boundaries['east'], combined_col_graph.boundaries['west'])
	mergeGraphs(combined_graph, combined_col_graph)
	combined_graph.boundaries['east'] = combined_col_graph.boundaries['east']

graph2img(combined_graph)
stitchTiles()