from flask import Flask, render_template, render_template_string
import d3fdgraph


app = Flask(__name__)

port = 8081



@app.route('/', methods=['GET'])
def index():
    links = [{"source": "apple", "target": "banana", "weight": 1, "type": '1'},
             {"source": "apple", "target": "orange", "weight": 2, "type": '1'},
             {"source": "banana", "target": "orange", "weight":3, "type": '1'},
             {"source": "banana", "target": "plum", "weight":3, "type": '2'},
             {"source": "orange", "target": "mango", "weight":3, "type": '1'},
             {"source": "kiwi", "target": "grape", "weight":3, "type": '2'}
    ]
    nodes = [ 
        {'id': 'orange', 'group': '1', 'size':3}, 
        {'id': 'mango', 'group': '1', 'size':0}, 
        {'id': 'plum', 'group': '2', 'size':2}, 
        {'id': 'kiwi', 'group': '2', 'color': 'green', 'size':1}, 
        {'id': 'grape', 'group': '1', 'color': 'purple', 'size':2},         
        {'id': 'apple', 'color': 'blue', 'image': 'http://fun.resplace.net/Emoticons/Food/Apple.gif', 'group': 3, 'size':1},
        {'id': 'banana', 'group': '1', 'color': 'yellow', 'size': 3, 'image': 'http://fun.resplace.net/Emoticons/Food/Banana.gif'}, 
        
    ]
    g=d3fdgraph.d3fdGraph(charge=-200, collision_scale=2)
    g.from_dict(links, nodes)
    g.set_node_color_by('group')

    g.set_node_radius_by('size')
    g.set_edge_color_by('type')
    div, script = g.plot_components()
    return '''
<html>
<body>
%s
%s
</body>
</html>
''' %(div, script)


if __name__ == '__main__':
  app.run(port=port, debug=True)
