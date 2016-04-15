var width = 960,
    height_title = 30,
    width_nav = 800,
    height_nav = 80,
    height_sunburst = 800,  // height of the sunburst plot
    radius = (Math.min(width, height_sunburst) / 2),
    height_panel1 = height_title + height_nav + height_sunburst + 50,
    height_title_wc = 30,
    height_nav_wc = 80,
    height_wc = 480,  // heigh of wordcloud
    height_panel2 = height_title_wc + height_nav_wc + height_wc,
    height_fig = height_panel1 + height_panel2
    ;

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
.attr("y",height_title)
.style("font-size", "24px")
.attr("text-anchor", "middle");

svg.append('text')
.text('Abstract Word Cloud by topic')
.attr("x",width/2)
.attr("y",height_panel1 + height_title_wc)
.style("font-size", "24px")
.attr("text-anchor", "middle");


// add navigation bar
var nav = svg.append('foreignObject')
.attr('id', 'nav')
.attr("text-anchor", "middle")
.attr('x', (width-width_nav)/2 )
.attr('y', height_title)
.attr('width', width_nav)
.attr('height', height_nav)
;

// add navigation bar for wordcloud
var nav_wc = svg.append('foreignObject')
.attr('id', 'nav')
.attr("text-anchor", "middle")
.attr('x', (width-width_nav)/2 )
.attr('y', height_panel1)
.attr('width', width_nav)
.attr('height', height_nav)
;

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
        d.color = d.name=='root' ? '#ffffff' : d3.hsl( d.hue, d.saturation, 0.6);
    })

    // if output partition object to console
    if (false) {console.log(data_partition);}

    var g = svg.append('g')
    .attr('id','sunburst')
    .attr("transform", "translate(" + width / 2 + "," + ( height_title + height_nav +  height_sunburst/2) + ")")
    .selectAll("g")
    .data(data_partition)
    .enter().append("g");

    var path = g.append("path")
    .attr("d", arc)
    .style("fill", function(d){return d.color;})
    .style("stroke", "#fff")
    .append("title")
    .text(function(d) { return d.fullname + "\ncount=" + formatNumber(d.value); });

    // Add label on every arc
    // use "foreignObject" and html to achieve text-wrap
    var arc_label = g.append("foreignObject")
    .attr("transform", function(d) { return "rotate(" + computeTextRotation(d) + ")"; })
    .attr('width', function(d){ return (y(d.y+d.dy)-y(d.y))*0.9; })
    .attr('height', function(d){
        d.text_height = (x(d.x+d.dx)-x(d.x))*0.9*y(d.y);
        return d.text_height; })
    .attr("x", function(d) { return y(d.y+d.dy*0.05); })
    .attr('y', function(d) { return -0.5*d.text_height; })
    .attr('class', 'arc_label')
    // use html <div> component to to show text with wrap and vertical-alingned
    .html(function(d) {
        return d.dx>5/360 & d.name != 'root'
        ? '<div><div class="arc_label_text">'+d.fullname+'</div></div>'
        : '<div><div class="arc_label_text">'+'</div></div>'; })
    // use two <div> as table format to achieve vertical-align
    .style('font-size', '11px')
    .select('div')
    .style('display', 'table')
    .select('div')
    .style('display', 'table-cell')
    .style('height', function(d){return d.text_height+'px';})
    .style('vertical-align', 'middle')
    // .style('border','1px solid black')
    ;

    // mouse trigger
    g
    .on('mouseover',mouseOverArc)
    .on('mouseout' ,mouseOutArc)
    .on("click", click)  // mouse click call back
    .on("dblclick", dblclick)  // mouse click call back

    // ++++++++++ navigation bar ++++++++++
    var depth_max = Math.max(...data_partition.map(function(d){return d.depth;}));
    nav.html('<table>'+ '<td></td>'.repeat(depth_max) +'</table>')
    .select('table')
    .attr('id','nav_table')
    .attr('width' ,width_nav)
    .attr('height',height_nav)
    .selectAll('td')
    .attr('width',width_nav/depth_max)
    .attr('bgcolor','AliceBlue')
    .style('border','1px solid silver')
    ;

    nav_wc.html('<table>'+ '<td></td>'.repeat(depth_max) +'</table>')
    .select('table')
    .attr('id','nav_table')
    .attr('width' ,width_nav)
    .attr('height',height_nav)
    .selectAll('td')
    .attr('width',width_nav/depth_max)
    .attr('bgcolor','AliceBlue')
    .style('border','1px solid silver')
    ;

    // ++++++++++ mouse interaction ++++++++++
    function click(d) {
        // update navigation bar for wc
        var object_hirch = getLabelHierarchy(d);  // get label text
        var td_all = nav_wc.selectAll('table').selectAll('td')[0];  // get nav bar table cells
        // update table cells
        for (i=0; i<td_all.length; i++){
            if (i<object_hirch.length){ // from root to current level
                td_all[i].innerText = object_hirch[i].fullname;
                // td_all[i].attr('bgcolor', 'blue');
                td_all[i].bgColor = d3.hsl( object_hirch[i].hue, object_hirch[i].saturation, (i==object_hirch.length-1 ? 0.6 : 0.9) );
            }
            else {
                td_all[i].innerText = null;
                td_all[i].bgColor = 'Snow';
            }
        }
    }

    // mouse click function
    function dblclick(d) {
        g.selectAll('.arc_label').attr("opacity", 0);

        click_tran = svg.transition()
        .duration(750)
        .selectAll("path")
        .attrTween("d", arcTween(d))
        .each("end", function(e, i) {
            // get a selection of the associated text element
            var arcText = d3.select(this.parentNode).select("foreignObject");
            // recalculate positions
            arcText
            .attr("transform", function() { return "rotate(" + computeTextRotation(e) + ")" })
            .attr('width', function(e){ return (y(e.y+e.dy)-y(e.y))*0.9; })
            .attr('height', function(e){
                e.text_height = (x(e.x+e.dx)-x(e.x))*0.9*y(e.y);
                return e.text_height; })
            .attr("x", function(e) { return y(e.y+e.dy*0.05); })
            .attr('y', function(e) { return -0.5*e.text_height; })
            ;

            // update the html text
            arcText.select('div').select('div')
            .style('height', function(e){return e.text_height+'px';})
            [0][0].innerText = (  // [0][0] to select from array
                (e.x>=d.x & e.x<(d.x+d.dx) & (x(e.x+e.dx)-x(e.x))/Math.PI*180>5
                & e.name != 'root')
                ? e.name
                : null );

            arcText.attr("opacity", 1);;

        })
    }

    //
    function mouseOverArc(d) {
        // update arc
    	d3.select(this).attr("stroke-width","4");
        d3.select(this).select('path')
        .style('fill',function(d){return d3.hsl( d.hue, d.saturation, 0.8)});

        // update navigation bar
        var object_hirch = getLabelHierarchy(d);  // get label text
        var td_all = nav.selectAll('table').selectAll('td')[0];  // get nav bar table cells
        // update table cells
        for (i=0; i<td_all.length; i++){
            if (i<object_hirch.length){
                td_all[i].innerText = object_hirch[i].fullname;
                // td_all[i].attr('bgcolor', 'blue');
                td_all[i].bgColor = d3.hsl( object_hirch[i].hue, object_hirch[i].saturation, (i==object_hirch.length-1 ? 0.6 : 0.90) );
            }
            else {
                td_all[i].innerText = null;
                td_all[i].bgColor = 'Snow';
            }
        }
    }
    function mouseOutArc(d) {
    	d3.select(this).attr("stroke-width","1");
        d3.select(this).select('path')
        .style('fill', function(d){return d.color;} );
    }

    // ++++++++++ topic tree ++++++++++
    svg.append('g')
    .attr('id','label_tree')
    .attr('transform', "translate(" + 0 + "," + height_title + ")");

    svg.append('g')
    .attr('id','label_tree')
    .attr('transform', "translate(" + 0 + "," + (height_title+height_nav+height_sunburst) + ")");

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


function getLabelHierarchy(d) {
    label_hirch = [];
    hue_hirch = [];
    object_hirch = [];
    c = d;
    while (c.name != 'root'){
        label_hirch.push(c.fullname);
        hue_hirch.push(c.hue);
        object_hirch.push(c)
        c = c.parent;
    }
    return object_hirch.reverse();
}
