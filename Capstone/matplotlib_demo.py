"""
Matplotlib binpack demo
"""
from typing import List, Tuple
from random import randint
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, Patch
import matplotlib.pyplot as plt

from item import Item

from binmanager import BinManager


def get_vertices(i: Item, margin: int = 0.0) -> List:
    corners = [(i.x, i.y), 
            (i.x+i.width, i.y),
            (i.x+i.width, i.y+i.height),
            (i.x, i.y+i.height)]
    if margin:
        scalar = margin
        corners = [(i.x + scalar, i.y + scalar), 
                   (i.x + i.width - scalar, i.y + scalar),
                   (i.x + i.width - scalar, i.y + i.height - scalar),
                   (i.x + scalar, i.y + i.height - scalar)]
    return corners

def generate_path(i: Item, margin: float = 0.0) -> Path:
    vertices = []
    codes = []
    codes += [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
    vertices += get_vertices(i, margin) + [(0, 0)]

    vertices = np.array(vertices, float) 
    return Path(vertices, codes)

#def generate_path(items: List[g.Item], margin: bool = False) -> Path:
#    vertices = []
#    codes = []
#    for i in items:
#        codes += [Path.MOVETO] + [Path.LINETO]*3 + [Path.CLOSEPOLY]
#        vertices += get_vertices(i, margin) + [(0, 0)]
#
#    vertices = np.array(vertices, float) 
#    return Path(vertices, codes)

def draw_wastemap(binpack: BinManager) -> None:
    path = generate_path(binpack.bins[0].wastemap.freerects)            
    return PathPatch(path, lw=2.0, fc='white', edgecolor='orange', hatch='/',  label='wastemap')
    

def render_bin(binpack: BinManager, save: bool = False) -> None:
    fig, ax = plt.subplots()
    for item in binpack.items:
        path = generate_path(item)
        packed_item = PathPatch(path, facecolor='blue', edgecolor='green', label='packed items')
        ax.add_patch(packed_item)
    handles = [packed_item]
    
    if binpack.pack_algo == 'shelf':
        vertices = []
        codes = []
        for shelf in binpack.bins[0].shelves:
            codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
            vertices += [(0, shelf.vertical_offset), (shelf.x, shelf.vertical_offset), (0, 0)]
        vertices = np.array(vertices, int)
        path = Path(vertices, codes)
        shelf_border = PathPatch(path, lw=2.0, fc='red', edgecolor='red', label='shelf')
        handles.append(shelf_border)
        ax.add_patch(shelf_border)

    if binpack.pack_algo == 'skyline':
        vertices = []
        codes = []
        for seg in binpack.bins[0].skyline:
            codes += [Path.MOVETO] + [Path.LINETO] + [Path.CLOSEPOLY]
            vertices += [(seg.x, seg.y), (seg.x+seg.width, seg.y), (0, 0)]
        vertices = np.array(vertices, int)
        path = Path(vertices, codes)
        skyline = PathPatch(path, lw=2.0, fc='red', edgecolor='red', label='skyline')
        ax.add_patch(skyline)
        handles.append(skyline)

        wastemap = draw_wastemap(binpack)
        handles.append(wastemap)
        ax.add_patch(wastemap)
    
    if binpack.pack_algo == 'guillotine':
        path = generate_path(binpack.bins[0].freerects, True)
        freerects = PathPatch(path, fc='none', edgecolor='red', hatch='/', lw=1, label='freeRectangles')
        ax.add_patch(freerects)
        handles.append(freerects)
            
    if binpack.pack_algo == 'maximal_rectangle':
        margin = 0.04
        for rect in binpack.bins[0].freerects:
            path = generate_path(rect, margin=margin)
            freerects = PathPatch(path, fc='none', ec='red', lw=1, label='freeRectangles')
            ax.add_patch(freerects)
            margin += .02
        handles.append(freerects)
        
    ax.set_title('%s Algorithm - %r Heuristic' % (M.pack_algo, M.heuristic))
    ax.set_xlim(0, M.bin_width)
    ax.set_ylim(0, M.bin_height)
    
    plt.legend(handles=handles, bbox_to_anchor=(1.04,1), loc="upper left")


    if save:
        plt.savefig('%s Algorithm - %r Heuristic' % (M.pack_algo, M.heuristic), bbox_inches="tight", dpi=150)
    else:
        plt.show()
    return


if __name__ == '__main__':
    #M = BinManager(10, 6, pack_algo='maximal_rectangle', heuristic='bottom_left', rotation=False, sorting=False)
    #M = BinManager(10, 6, pack_algo='guillotine', heuristic='best_shortside', rotation=False, sorting=False)
    #M = BinManager(10, 6, pack_algo='shelf', heuristic='next_fit', rotation=False, sorting=False)
    M = BinManager(10, 6, pack_algo='skyline', heuristic='bottom_left', rotation=False, sorting=False)
    maximal = [Item(2,3,'Item A'), Item(3,3,'Item B'), Item(4,1,'Item C'), Item(2,3,'Item D'), Item(2,2,'Item E'), Item(1,2,'Item F')]
    M.add_items(*maximal)
    M.execute()
    print(maximal)
    print(M.bins)
    render_bin(M, save=False)

