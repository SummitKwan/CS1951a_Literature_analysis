var width = 960,
    height = 960,  // height of the sunburst plot
    edge_sunburst = 50,
    radius = (Math.min(width, height) / 2) - edge_sunburst;
var height_wc = 480,  // heigh of wordcloud
    height_fig= height + height_wc;

var formatNumber = d3.format(",d");

var x = d3.scale.linear()
.range([0, 2 * Math.PI]);

var y = d3.scale.linear()  // use linear scale to make the center spot smaller
.range([0, radius]);

var color = d3.scale.category20c();

var partition = d3.layout.partition()  // set up a build-in partition object
.value(function(d) { return d.size; })
.sort(function (a,b){return d3.ascending(a.name,b.name);});  // sort by name

var arc = d3.svg.arc()  // set up arc object
.startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x))); })
.endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x + d.dx))); })
.innerRadius(function(d) { return Math.max(0, y(d.y)); })
.outerRadius(function(d) { return Math.max(0, y(d.y + d.dy)); });

// creat svg, append to html element
var svg = d3.select("#topic_view").append("svg")
.attr("width", width)
.attr("height", height_fig);

// add title text to figure
svg.append('text')
.text('SfN 2016 conference abstracts by topic')
.attr("x",width/2)
.attr("y",30)
.style("font-size", "24px")
.attr("text-anchor", "middle");

d3.json("topic_tree.json", function(error, root) {
    if (error) throw error;

    // get partition object from the tree stucture, key for this plot
    var data_partition = partition.nodes(root);

    // calculate color, children nodes share the color of their parent node
    data_partition.forEach(function (d){
        d.saturation = d3.scale.linear().domain([0, 1]).range([1,0.5])
            (d.y);
        if (d.name=='root'){d.hue = 180;}
        else if (d.parent.name=='root') {
            d.hue = (d.x+d.dx/2)/d.parent.dx*360;}
        else {  // take the diff from parent, normalized, scaled (1/5), and add parent value
            d.hue = ( (d.x+d.dx/2-d.parent.x-d.parent.dx/2)/d.parent.dx*360)/5+d.parent.hue ;}
        d.color = d.name=='root' ? '#ffffff' : d3.hsl( d.hue, d.saturation, 0.5);
    })

    // if output partition object to console
    if (false) {console.log(data_partition);}

    var g = svg.append('g')
    .attr('id','sunburst')
    .selectAll("g")
    .data(data_partition)
    .enter().append("g")
    .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");

    var path = g.append("path")
    .attr("d", arc)
    .style("fill", function(d){return d.color;})
    .style("stroke", "#fff")
    .append("title")
    .text(function(d) { return d.name + "\ncount=" + formatNumber(d.value); });

    var text = g.append("text")
    .attr("transform", function(d) { return "rotate(" + computeTextRotation(d) + ")"; })
    .attr('text_width', function(d){ return (y(d.y+d.dy)-y(d.y))*0.9; })
    .attr('text_height', function(d){ return (x(d.x+d.dx)-x(d.x))*0.9; })
    .attr("x", function(d) { return y(d.y+d.dy*0.05); })
    .attr('id', 'arc_label')
    .text(function(d) { return d.dx>5/360 & d.name != 'root' ? d.name : null; })
    .style('font-size', '11px')
    .call(text_wrap);

    // g.append("foreignObject")
    // .attr("transform", function(d) { return "rotate(" + computeTextRotation(d) + ")"; })
    // .attr('width', function(d){ return (y(d.y+d.dy)-y(d.y))*0.9; })
    // .attr('height', function(d){ return (x(d.x+d.dx)-x(d.x))*0.9*y(d.y); })
    // .attr("x", function(d) { return y(d.y+d.dy*0.05); })
    // .attr('id', 'arc_label')
    // .html(function(d) { return d.dx>5/360 & d.name != 'root' ? '<div>'+d.name+'</div>' : null; })
    // // .style("display",'table-cell' )
    // // .style('vertical-align', 'middle') // not working
    // .style('font-size', '11px');

    g.selectAll('#arc_label').selectAll('div')
    .style('display','table-cell')
    .style('vertical-align','middle');

    // mouse trigger
    g
    .on('mouseover',mouseOverArc)
    .on('mouseout' ,mouseOutArc)
    .on("click", click)  // mouse click call back
    .on("dblclick", dblclick)  // mouse click call back

    function click(d) {
        labelHirch = getLabelHierarchy(d);
        current_label.html( labelHirch.join('</br>') );
    }

    // mouse click function
    function dblclick(d) {
        g.selectAll('#arc_label').attr("opacity", 0);

        click_tran = svg.transition()
        .duration(750)
        .selectAll("path")
        .attrTween("d", arcTween(d))
        .each("end", function(e, i) {
            // get a selection of the associated text element
            var arcText = d3.select(this.parentNode).select("text");
            // fade in the text element and recalculate positions
            arcText
            .attr("transform", function() { return "rotate(" + computeTextRotation(e) + ")" })
            .attr('text_width', function(){ return (y(e.y+e.dy)-y(e.y))*0.9; })
            .attr('text_height', function(){ return (x(e.x+e.dx)-x(e.x))*0.9; })
            .attr("x", function() { return y(e.y+e.dy*0.05); })
            ;

            arcText.transition().duration(200).attr("opacity", 1);

            // check if the animated element's data e lies within the visible angle span given in d
            if (e.x >= d.x && e.x < (d.x + d.dx)) {
                arcText.text(function(e) { return (x(e.x+e.dx)-x(e.x))/Math.PI*180>5 & e.name != 'root' ? e.name : null; });
                text_wrap(arcText);
            }
            else {
                arcText.text( null );
            }
        })
    }

    // ++++++++++ topic tree ++++++++++
    svg.append('g')
    .attr('id','label_tree')
    .attr('transform', "translate(" + 0 + "," + edge_sunburst + ")");

    svg.append('g')
    .attr('id','label_tree')
    .attr('transform', "translate(" + 0 + "," + height + ")");

    // use forign object to add html text with multiple lines
    var current_label = svg.selectAll('#label_tree').append('foreignObject')
    .attr('width', width)
    .attr('height',100)
    .html('');

});

// ########## tool functions ##########
// Interpolate the scales by adjusting the x,y scalling function
function arcTween(d) {
    var xd = d3.interpolate(x.domain(), [d.x, d.x + d.dx]),
        yd = d3.interpolate(y.domain(), [d.y, 1]),
        yr = d3.interpolate(y.range(), [d.y ? 20 : 0, radius]);
    return function(d, i) {
        return i
        ? function(t) { return arc(d); }
        : function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); return arc(d); };
    };
}

// compute angle of text label for arcs
function computeTextRotation(d) {
    return (x(d.x + d.dx / 2) - Math.PI / 2) / Math.PI * 180;
}

// text wrap for labels, from https://bl.ocks.org/mbostock/7555321
function text_wrap(text) {
  text.each(function() {
    var text = d3.select(this),
        words = text.text().split(/\s+/).reverse(),
        word,
        line = [],
        lineNumber = 0,
        lineHeight = 1.1, // ems
        text_width = text.attr("text_width"),
        text_height = text.attr("text_height"),
        x = text.attr("x"),
        y = text.attr("y"),
        tspan = text.text(null).append("tspan");
    while (word = words.pop()) {
      line.push(word);
      tspan.text(line.join(" "));
      if (tspan.node().getComputedTextLength() > text_width) {
        line.pop();
        tspan.text(line.join(" "));
        line = [word];
        if (lineNumber * lineHeight < text_height/2 ){  // to prevent the text from going out of the arc
            tspan = text.append("tspan").attr("x", x).attr("y", ++lineNumber * lineHeight + "em").text(word);
        }
      }
    }
  });
}

//
function mouseOverArc() {
	d3.select(this).attr("stroke-width","4");
    d3.select(this).select('path')
    .style('fill',function(d){return d3.hsl( d.hue, d.saturation, 0.8)});
}
function mouseOutArc() {
	d3.select(this).attr("stroke-width","1");
    d3.select(this).select('path')
    .style('fill', function(d){return d.color;} );
}

function getLabelHierarchy(d) {
    label_hirch = [];
    hue_hirch = [];
    c = d;
    while (c.name != 'root'){
        label_hirch.push(c.name);
        hue_hirch.push(c.hue);
        c = c.parent;
    }
    return label_hirch.reverse();
}
