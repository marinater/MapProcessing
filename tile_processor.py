import os
import cv2
import numpy as np
import uuid as uuid_lib
from skimage.morphology import skeletonize
from skimage.measure import label
from scipy.ndimage import center_of_mass

class Node:
	def __init__(self, tile_id, id, conn, pos):
		self.tile_id = tile_id
		self.id = id
		self.connected = { c for c in conn }
		self.position = pos

	def __repr__(self):
		return 'Node {}:\n\t{}\n'.format(self.id[-5:], [x[-5:] for x in self.connected])

class Graph:
	def __init__(self, tile_id=None, pos_offset=None, filename=None, boundary_graph=None, boundaries=None):
		self.boundary_graph = {}
		self.boundaries = {'north':[], 'south':[], 'east':[], 'west':[]}
		self.node_image = None
		self.pos_offset = pos_offset

		if filename != None:
			# Load and binarize image
			original = cv2.imread(filename, cv2.IMREAD_GRAYSCALE)
			_, original = cv2.threshold(original, 30, 1, cv2.THRESH_BINARY)
			# Retrieve intersections and endpoints
			nodes = self.get_nodes(original)
			# Generate graphs from node information
			self.generate_boundary_graph(nodes, original, tile_id)
		else:
			if boundary_graph:
				self.boundary_graph = boundary_graph
			if boundaries:
				self.boundaries = boundaries

	def isolate_nodes(self, skeleton):
		skeleton[skeleton > 0] = 1
		skeleton = skeleton.astype(np.uint8)
		
		# Set every pixel to be 10 + number of neighbors
		kernel = np.uint8([[1, 1, 1], [1, 10, 1], [1, 1, 1]])
		filtered = cv2.filter2D(skeleton, -1, kernel, borderType=cv2.BORDER_CONSTANT)

		# Remove pixels in the middle of a line (have 2 neighbors)
		out = np.zeros(skeleton.shape, dtype=np.uint8)
		out[ (filtered == 11) | (filtered > 12) ] = 1

		return out

	def get_nodes(self, img):
		# Reduce thickness of lines to 1 pixel
		skeleton = skeletonize(img)
		# Retrieve image of only endpoints and intersections
		raw_nodes = self.isolate_nodes(skeleton)
		# Get the top left corner of every node cluster
		labeled_nodes, node_count = label(raw_nodes, return_num=True)
		nodes = [
			tuple(np.argwhere(labeled_nodes == val)[0])
			for val in range(1, node_count + 1)
		]
		return nodes

	def generate_boundary_graph(self, nodes, original, tile_id):
		# Create image to draw nodes
		self.node_image = np.zeros(original.shape, dtype=np.uint8)

		# Label all connected paths with the same distinct value
		# Used to determine which nodes are connected
		labeled_roads, road_count = label(original, return_num=True)

		# Used to track which entry/exit nodes are connected to each other
		boundary_connectivity = { val :[] for val in range(1, road_count + 1)}
		self.boundary_graph = {}

		height, width = original.shape
		for index, node in enumerate(nodes):
			node_uuid = uuid_lib.uuid4().hex
			# Determine if it is a boundary node and save if it is
			if node[0] < 3:
				self.boundaries['north'].append(node_uuid)
			elif node[1] < 3:
				self.boundaries['west'].append(node_uuid)
			elif node[0] > height - 3:
				self.boundaries['south'].append(node_uuid)
			elif node[1] > width - 3:
				self.boundaries['east'].append(node_uuid)
			else:
				self.node_image[node] = 80
				continue
			
			boundary_connectivity[ labeled_roads[node] ].append( (node_uuid, node) )
			self.node_image[node] = 255

		for connected_nodes in boundary_connectivity.values():
			for index in range(len(connected_nodes)):
				conn = [v[0] for v in connected_nodes[0: index]] + [v[0] for v in connected_nodes[ index + 1 :]]
				id, pos = connected_nodes[index]
				pos = (self.pos_offset[0] + pos[0], self.pos_offset[1] + pos[1])
				
				self.boundary_graph[ id ] = Node(tile_id, id, conn, pos)
		
		self.boundaries['north'].sort(key= lambda uid: self.boundary_graph[uid].position[1])
		self.boundaries['south'].sort(key= lambda uid: self.boundary_graph[uid].position[1])
		self.boundaries['east'].sort(key= lambda uid: self.boundary_graph[uid].position[0])
		self.boundaries['west'].sort(key= lambda uid: self.boundary_graph[uid].position[0])
	
	def __repr__(self):
		out = ''
		for key, val in self.boundary_graph.items():
			out += str(val)
		
		return out
