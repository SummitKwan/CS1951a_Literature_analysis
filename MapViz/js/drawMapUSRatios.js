var bubbleScale = 1.25;
var arcScale = 0.001;


function drawMap(bubbleArray, arcsArray) {
	var map = new Datamap({
		element: document.getElementById('map'),
		scope: 'usa',
		fills: {
			research: '#dd2222',
			defaultFill: '#ABDDA4'
		}
	});

	map.bubbles(bubbleArray, {
		popupTemplate: function(geo, data) {
			var currArcs = arcsArray.filter(function(arc) {
				return (arc.origin.latitude == data.latitude &&
					arc.origin.longitude == data.longitude) ||
					(arc.destination.latitude == data.latitude &&
					arc.destination.longitude == data.longitude);
			});
			map.arc(currArcs);
			return [
				'<div class="hoverinfo">' + data.location,
				'<br/>' + data.reln_count + ' relationships',
				'<br/>' + data.poster_count + ' posters',
				'<br/>Ratio: ' + (data.reln_count / Math.max(data.poster_count, 1)).toFixed(2),
				'</div>'
			].join('');
		}
	});

	map.svg.selectAll('.bubbles').on('mouseout', function(geo) {
		map.arc(arcsArray);
	})

	map.arc(arcsArray);

}

$(function() {
	d3.csv('./data/researchLocnsUS.csv', function(countData) {
		d3.csv('./data/arcsUS.csv', function(arcsData) {
			drawMap(countData.map(function(d) {
				return {
					latitude: +d['latitude'],
					longitude: +d['longitude'],
					radius: (Math.sqrt((+d['relation_count']) / (+d['poster_count'])) * bubbleScale).toFixed(2),
					fillKey: 'research',
					location: d['location'],
					borderWidth: 0.5,
					borderColor: '#006',
					fillOpacity: 1,
					poster_count: +d['poster_count'],
					reln_count: +d['relation_count']
				};
			}),
			arcsData.map(function(d) {
				var count = +d['count'];
				var alpha = Math.pow(count, .3) / 8;
				return {
					origin: {
						latitude: +d['lat1'],
						longitude: +d['lon1']
					},
					destination: {
						latitude: +d['lat2'],
						longitude: +d['lon2']
					},
					options: {
						strokeWidth: count * arcScale,
						strokeColor: 'rgba(0, 0, 200, ' + alpha + ')',
						greatArc: true
					}
				};
			}));
		});
	});
});
