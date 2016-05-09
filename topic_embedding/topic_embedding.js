// todo:
//   double click for touch device
//   move wordcloud with mouse click

var width = 800,
    height= 800;

var formatNumber = d3.format(",d");

var color = d3.scale.category10();

// creat svg, append to html element
var svg = d3.select("#topic_embedding").append("svg")
.attr("width", width)
.attr("height", height)
.style('all','initial')
.style('font-family','"Trebuchet MS", Helvetica, sans-serif')
;

// add title text to figure
svg.append('text')
.text('Anatomy of SfN 2015 research topics')
.attr("x",width/2)
.attr("y",20)
.style("font-size", "24px")
.attr("text-anchor", "middle");

var tooltip = d3.select("#topic_embedding")
    .append("div")
    .attr("class", "tooltip")
    .style("position", "absolute")
    .style("opacity", 0)
    .style("background", "lightsteelblue")
    .style("width", "200px")
    .style("padding", '10px')
    .style("border-radius", "10px")
    .style("stroke", "black")
    ;

// var tooltip_html = svg.append('foreignObject')
// .attr('x', 0)
// .attr('y', 0)
// .attr('width', 200)
// .attr('height', 200)
// .style("opacity", 1)
// .html('<div>hahah</div>')
// .style('font-size','12px')
// .style("background", "lightsteelblue")
// .style("border-radius", "10px")
// .style("stroke", "black")
// ;



var static_tooltip = svg.append('text')
.text('')
.attr("x",0)
.attr("y",50);

d3.json("topic_embedding.json", function(error, data) {
    if (error) throw error;

    all_x = data.map( function(d){return d.x} ) ;
    x_max = d3.max( all_x );
    x_min = d3.min( all_x );

    all_y = data.map( function(d){return d.y;} );
    y_max = d3.max( all_y );
    y_min = d3.min( all_y );

    var x = d3.scale.linear()
    .domain([x_min, x_max])
    .range([-width/2.5,width/2.5])
    ;

    var y = d3.scale.linear()  // use linear scale to make the center spot smaller
    .domain([y_min, y_max])
    .range([height/2.5, -height/2.5])
    ;

    var g = svg.append('g')
    .attr('id','scatter_plot')
    .attr("transform", "translate(" + width/2 + "," + height/2 +")")
    .selectAll("g")
    .data(data)
    .enter();

    g.append("circle")
    .attr("class", "dot")
    .attr("r", function(d) {return 30/Math.pow(1.8,d.h);} )
    .attr("cx", function(d) { return x(d.x); })
    .attr("cy", function(d) { return y(d.y); })
    .style("fill", function(d) { return d3.rgb(d.ch); })
    .style("stroke", "#D0D0D0")
    .style("stroke-width", "2")
    .style("opacity", function(d){return Math.pow(0.8,d.h-1);})
    .on("mouseover", function(d) {
        var cursor_in_svg = d3.mouse(svg.node());

        d3.select(this)
        .style('fill', function(d) { return d3.rgb(d.ch).darker(1); } );

        tooltip_html
        .style('opacity',0.8)
        .html(d.yh)
        ;

        // tooltip.transition()
        //     .duration(200)
        //     .style("opacity", .8)
        //     // .style("left", (x(d.x) +20) + "px")
        //     .style("left", (cursor_in_svg[0] ) + "px")
        //     .style("top",  (cursor_in_svg[1] ) + "px")
        // tooltip.html( d.yh );
        static_tooltip.text(d.yh)
        .style("fill", d3.rgb(d.ch).darker(1));
        })
    .on("mouseout", function(d) {
        d3.select(this)
        .style('fill', function(d) { return d3.rgb(d.ch); } );
        // tooltip.html('');
        // tooltip.transition()
        //     .duration(200)
        //     .style("opacity", .0);
        });
    // .append("title")
    // .text(function(d) { return d.yh; })
    ;




    // mouse trigger

    // ++++++++++ mouse interaction ++++++++++

});

// ########## tool functions ##########
