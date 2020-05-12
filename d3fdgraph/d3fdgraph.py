import copy
import uuid
import random
import colorsys

import jinja2
import networkx
import IPython.core.display
from .d3Templates import d3fdTemplate



def get_N_HexCol(N=5):
    HSV_tuples = [(x * 1.0 / N, 0.5, 0.5) for x in range(N)]
    hex_out = []
    for rgb in HSV_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        hex_out.append('#%02x%02x%02x' % tuple(rgb))
    return hex_out


class d3fdGraph(d3fdTemplate):
    
    def __init__(self,
                 imgsize=(800, 600), 
                 node_radius=15, 
                 link_distance=20, 
                 collision_scale=1.5, 
                 link_width_scale=4,
                 charge = -20
    ):
        self._attrs={
            'imgwidth': imgsize[0],
            'imgheight': imgsize[1],
            'node_radius': node_radius,
            'link_distance': link_distance,
            'collision_scale': collision_scale,
            'link_width_scale': link_width_scale,
            'charge': charge
        }
        
        self._edges = []
        self._nodes = {}

    @property
    def attrs(self):
        return self._attrs

    def add_node(self, node_dict):
        if 'id' not in node_dict.keys():
            node_dict['id'] = str(uuid.uuid4())
        if 'label' not in node_dict.keys():
            node_dict['label'] = node_dict['id']
        if node_dict['id'] in self.node_ids:
            raise('repeated node definition')
        node_dict['radius'] = node_dict.get('radius', 0)
        self._nodes[node_dict['id']] = node_dict

    def add_edge(self, edge_dict):
        for nid in ('source', 'target'):
            if nid not in edge_dict.keys():
                raise('Wrong edge definition. Missing attr "%s"' % nid)
            if edge_dict[nid] not in self.node_ids:
                self.add_node({'id': edge_dict[nid]})
        self._edges.append(edge_dict)

    def set_node_color_by(self, group_key, hist_bins=None):
        # TODO: Histograms
        colormap = {}
        categories = set(map(lambda x: x.get(group_key, None), self.nodes))
        colors = get_N_HexCol(len(categories))
        to_color=dict(zip(categories, colors))
        for n in self.nodes:
            n['color'] = to_color[n.get(group_key, None)]
            
    def set_edge_color_by(self, group_key, hist_bins=None):
        # TODO: Histograms
        colormap = {}
        categories = set(map(lambda x: x.get(group_key, None), self.edges))
        colors = get_N_HexCol(len(categories))
        to_color=dict(zip(categories, colors))
        for n in self.edges:
            n['color'] = to_color[n.get(group_key, None)]

    def set_node_radius_by(self, group_key):
        radius = list(map(lambda x: x[group_key], self.nodes))
        M=max(radius)
        m=min(radius)
        if M-m == 0:
            M+=1
        for n in self.nodes:
            n['radius'] = self._attrs['node_radius']*(1.5*(n[group_key]-m)/(M-m))

    def normalize_weights(self):
        try:
            M = max(map(lambda x: x.get('weight', 1), self._edges))
        except:
            M=1
        for i in self._edges:
            i['weight'] /= M

    @property
    def edges(self):
        self.normalize_weights()
        for i in self._edges:
            o='%s --(%s)--> %s' % (i['source'], i.get('weight', 0), i['target'])
            for j in i.keys():
                if j not in ('source', 'target', 'hover', 'weight', 'color'):
                    o+='\n %s ->\t %s' % (j, i[j])
            i['hover'] = o
        return self._edges

    @property
    def node_ids(self):
        return self._nodes.keys()
    
    @property
    def nodes(self):
        nodelist = list(self._nodes.values())
        for i in nodelist:
            o='%s' % i.get('label', i['id'])
            for j in i.keys():
                if j not in ('hover', 'id', 'label', 'color', 'radius', 'image'):
                    o+='\n %s ->\t %s' % (j, i[j])
            i['hover'] = o
        return nodelist

    def from_networkx(self, nxgraph):
        self._edges = []
        self._nodes = []
        graph_json = networkx.readwrite.json_graph.node_link_data(nxgraph)

    def from_dict(self, edgelist, nodelist=None):
        
        self._edges = []
        self._nodes = {}
        if nodelist is not None:
            for i in nodelist:
                self.add_node(copy.copy(i))
        for i in edgelist:
            self.add_edge(copy.copy(i))

    def from_pandas(self, node1_node1_weight):
        
        # convert node1_node1_weight to graph
        graph = networkx.from_pandas_edgelist(node1_node1_weight, source='source', target='target', edge_attr='weight')

        graph_json = networkx.readwrite.json_graph.node_link_data(graph)
        graph_json_nodes = graph_json['nodes']
        graph_json_links = graph_json['links']
        for link in graph_json_links:
            self.add_edge(link)
    
    @property
    def data(self):
        return {'config': self.attrs,
            'nodes': list(self.nodes),
            'links': list(self.edges)
        }
    @property
    def js(self):
        return self._js.render(**self.data)
    
    @property
    def html(self):
        return self._html.render(**self.data)

    def set_unique_id(self, uid):
        if uid is None:
            uid = str(uuid.uuid4())
        self._attrs['unique_id'] = uid 
    
    def nbplot(self, uid=None):
        self.set_unique_id(uid)
        # display html in notebook cell
        IPython.core.display.display_html(IPython.core.display.HTML(self.html))

        # display (run) javascript in notebook cell
        IPython.core.display.display_javascript(IPython.core.display.Javascript(data=self.js))

def plot_force_directed_graph(node1_node1_weight, node_radius=15, link_distance=20, collision_scale=4, link_width_scale=4, charge=-20):
    g=d3fdGraph( node_radius=node_radius, link_distance=link_distance, collision_scale=collision_scale, link_width_scale=link_width_scale, charge=charge)
    g.from_pandas(node1_node1_weight)
    g.nbplot()
