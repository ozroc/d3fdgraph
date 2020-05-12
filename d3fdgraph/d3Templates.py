import jinja2


class d3fdTemplate(object):
    _js = jinja2.Template('''
    // require is how jupyter manages javascript libraries
require.config({
    paths: {
        d3: 'https://d3js.org/d3.v5.min'
    }
});

require(["d3"], function(d3) {
    //console.log(d3.version);

    // size of plot
    const width = {{ config.imgwidth }};
    const height = {{ config.imgheight }};

    // node radius
    const node_radius = {{ config.node_radius }};
    // link distance before weight is applied
    const link_distance = {{ config.link_distance }};
    // collision exclusion sclae
    const collision_scale = {{ config.collision_scale }};
    // link with scale
    const link_width_scale = {{ config.link_width_scale }};

    // links and nodes data
    const links = {{ links }};
    const nodes = {{ nodes }};


    // create simulation
    const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id).distance(d => link_distance / d.weight))
    .force("charge", d3.forceManyBody().strength({{ config.charge }}))
    .force("collision", d3.forceCollide().radius(collision_scale * node_radius))
    .force("center", d3.forceCenter(width / 2, height / 2));

    /// dragging nodes
    const drag = simulation => {

        function dragstarted(d) {
        if (!d3.event.active) simulation.alphaTarget(0.5).restart();
            d.fx = d.x;
            d.fy = d.y;
        }

        function dragged(d) {
            d.fx = d3.event.x;
            d.fy = d3.event.y;
        }

        function dragended(d) {
        if (!d3.event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }

        return d3.drag()
          .on("start", dragstarted)
          .on("drag", dragged)
          .on("end", dragended);
    }

    // select HTML element and attach SVG to it
    const svg = d3.select("#d3-container-{{ config.unique_id }}")
        .append("svg")
        .attr("width", width)
        .attr("height", height);

    // add links to svg element
    const link = svg.append("g")
        .attr("class", "links")
        .selectAll("line")
        .data(links)
        .enter().append("line")
        .style("stroke", d => d.color)
        .style("stroke-width", d => 0.5+link_width_scale*d.weight);

    const llabel = link.append("title")
            .attr("dx", 10)
            .attr("dy", ".35em")
            .text(d => d.hover);

    const node = svg.append("g")
            .attr("class", "nodes")
        .selectAll("g")
        .data(nodes)
        .enter().append("g");

    const circle = node.append("circle")
            .style("stroke", function(d){ return d.color } )
            .style("fill", function(d){ return d.color } )
            .style("stroke-opacity", 1 )
            .style("fill-opacity", 0.2 )
            .attr("r", function(d){ return node_radius + d.radius })
            .on("dblclick", d => {d.x = width/2; d.y = height/2;})
            .call(drag(simulation));

    const image = node.append("image")
	  .attr("xlink:href", d=> d.image)
	  .attr("width", 24)
	  .attr("height", 24)
          .attr("dx", 12)
          .attr("dy", 12)
	  .call(drag(simulation));

    // svg text labels for eachnode
    const label = node.append("text")
            .attr("dx", 10)
            .attr("dy", ".35em")
            .text(d => d.id);

    const hlabel = node.append("title")
            .attr("dx", 10)
            .attr("dy", ".35em")
            .text(d => d.hover);


    // update svg on simulation ticks
    simulation.on("tick", () => {
        image
        // keep within edge of canvas, larger margin on right for text labels
            .attr("x", d => -12+(d.x = Math.max(2*12, Math.min(width - 2*12 - 10*d.id.length, d.x)) ))
            .attr("y", d => -12+(d.y = Math.max(2*12, Math.min(height - 2*12, d.y)) ));

        circle
        // keep within edge of canvas, larger margin on right for text labels
            .attr("cx", d => (d.x = Math.max(2*node_radius, Math.min(width - 2*node_radius - 10*d.id.length, d.x)) ))
            .attr("cy", d => (d.y = Math.max(2*node_radius, Math.min(height - 2*node_radius, d.y)) ));
        

        link
            .attr("x1", d => d.source.x)
            .attr("y1", d => d.source.y)
            .attr("x2", d => d.target.x)
            .attr("y2", d => d.target.y);

        hlabel
            .attr("x", d => 5+d.x)
            .attr("y", d => d.y);

        label
            .attr("x", d => 5+d.x)
            .attr("y", d => -10+d.y);
    });


    //return svg.node();

});
''') 
    _html = jinja2.Template('''
<script src="/static/components/requirejs/require.js"></script>
<div id="d3-container-{{ config.unique_id }}"></div>
<div>force-directed graph</div>

<style>
    .links line {
        stroke: #555;
        stroke-opacity: .8;
    }
    .nodes image {
        pointer-events: all;
    }

    .nodes circle {
        pointer-events: all;
        stroke: #555;
        fill: #555;
        stroke-width: 1.5px;
        opacity: 0.7;
    }
    .nodes text {
        pointer-events: none;
        font: 10px sans-serif;
        fill: #333;
        opacity: .5;
    }
    .nodes title {
        pointer-events: none;
        font: 10px sans-serif;
        fill: #fff;
        opacity: .25;
    }
</style>
''')
