# Map Processessing
Automatic HPA* Pipeline for Satellite Imagery
## Map Tile-Set Processing Pipeline
 - To use HPA*, we need to create multiple, in this case 2, hierarchies of graphs. The first is a set of intra-tile graphs and the second is a large inter-tile graph. The inter-tile graph is used to find the general route from point A to point B across tiles. The intra-tile graphs are then used to pick out the fastest route for each tile along that general route. The benefit of this is that it scales very well and should work on extremely large tile-sets.

To create an intra-tile graph:
 1. Load image and thin all roads to a uniform 1 pixel thickness
 2. Identify all intersections and endpoints as nodes
 3. Uniquely label connected components
 4. Connect all nodes with same label

To create inter-tile graph:
 1. Create an empty graph to store everything
 2. Load and merge all tiles in a column
	 1. Create an empty graph
	 2. Load a simplified intra-tile graph with only tile entrances and exits
	 3. Merge new graph with the combined column graph
	 4. Repeat
 3. Merge column graph with the combined graph
 4. Repeat for all columns

Merging graphs is done by keeping track of the nodes along the leading edges of the combined graph. When a new tile is being merged, overlapping nodes on the leading edge are combined. Connections to the deleted node are then updated to reflect the new node_id.

multi_tile_processor.py is used to create the combined graph and visualization for testing
tile_processor.py has Class definitions and creates the inter-tile graphs

## TO DO
Implement HPA* on the generated graphs