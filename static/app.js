// Lots of code from:
//  http://bl.ocks.org/dwtkns/4686432
//  http://mbostock.github.io/d3/talk/20111018/azimuthal.html
//  ideal: https://observablehq.com/@d3/versor-dragging

let colourPath    = "#1E88E510";
let colourSphere  = "#F8F8F8";
let colourLand    = "#AAA";
// D3 Map
// The svg
let svg = d3.select("svg")
          .classed("svg-container-map", true)
          .on("mousedown", mousedown)
          // .attr("width", 640)
          // .attr("height", 500)
          .attr("preserveAspectRatio", "xMinYMin meet")
          .attr("viewBox", "0 0 640 500");

// Map and projection
// projections: geoMercator, geoNaturalEarth1
let projection = d3.geoOrthographic()
  .scale(220)
  .translate([320,250])
  .clipAngle(90)
  .rotate([90,-45,0]);

// Path generator
let path = d3.geoPath()
    .projection(projection);

// Load world shape
d3.json("static/land-110m.json")
  .then(function(world) {

    var sphere = {type:"Sphere"};
  
    // Draw sphere
    svg.append("path")
      .datum(sphere)
      .attr("d", path)
      .attr("fill", colourSphere);

    // Draw map
    svg.insert("path", ".graticule")
        .datum(topojson.feature(world, world.objects.land))
        .attr("class", "land")
        .attr("fill", colourLand)
        .style("stroke", colourLand)
        .attr("d", path);

});

// Load flights data
var link;
d3.json("data.json")
  .then(function(data) {
  link = data;

  let lk = link[0];
  // Add paths
  svg.selectAll("myPath")
    .data(lk)
    .enter().append("path")
      .attr("class", "lines")  // need to specify class
      .attr("d", function(d){ return path(d)})
      .style("fill", "none")
      .style("stroke", colourPath)
      .style("stroke-width", 2);

  // Number of flights
  d3.select('#value-flights').text(lk.length);
});

d3.select(window)
  .on("mousemove", mousemove)
  .on("mouseup", mouseup);

let m0, o0;

function mousedown() {
  m0 = [d3.event.pageX, d3.event.pageY];
  o0 = projection.rotate();
  d3.event.preventDefault();
}

function mousemove() {
  if (m0) {
    let m1 = [d3.event.pageX, d3.event.pageY],
        o1 = [o0[0] + (m1[0] - m0[0]) / 6, o0[1] + (m0[1] - m1[1]) / 6];
    projection.rotate(o1);
    svg.selectAll("path")
     .attr("d", path);
    // refresh();
  }
}

function mouseup() {
  if (m0) {
    mousemove();
    m0 = null;
  }
}

// SLIDER    
 // Time
let dataTime = d3.range(1, 32);

let sliderTime = d3
  .sliderBottom()
  .min(1)
  .max(31)
  .step(1)
  .width(svg.attr("width") - 60)
  // .tickFormat(d3.timeFormat('%Y'))
  .tickValues(dataTime)
  .default(1)
  .on('onchange', val => {

    d3.select('#value-time').text(val);
    d3.select('#value-time-sup').text(`${nth(sliderTime.value())}`);

    // remove lines with old data
    svg.selectAll(".lines")
      // if you want a transition:
      // .transition();
      // .duration(100)
      // .style("opacity", 0)
      .remove();

    // add lines with new data
    let lk = link[val-1];
    svg.selectAll("myPath")
      .data(lk)
      .enter().append("path")
        .attr("class", "lines")  // need to specify class
        .attr("d", function(d){ return path(d)})
        .style("fill", "none")
        .style("stroke", colourPath)
        .style("stroke-width", 2);

    d3.select('#value-flights').text(lk.length);
  });

let gTime = d3
  .select('#slider-time')
  .classed("svg-container", true) 
  .append('svg')
  // Responsive SVG needs these 2 attributes and no width and height attr.
  .attr("preserveAspectRatio", "xMinYMin meet")
  .attr("viewBox", "0 0 640 100")
  // Class to make it responsive.
  .classed("svg-content-responsive", true)
  .append('g')
  .attr('transform', 'translate(30,30)');

gTime.call(sliderTime);

// Day format
const nth = function(d) {
  if (d > 3 && d < 21) return 'th';
  switch (d % 10) {
    case 1:  return "st";
    case 2:  return "nd";
    case 3:  return "rd";
    default: return "th";
  }
}
d3.select('#value-time').text(sliderTime.value());
d3.select('#value-time-sup').text(nth(sliderTime.value()));

if (link) d3.select('svg#myPath').data(link[sliderTime.value()]);

// Controls
var t;
function myCounter() {
  t = sliderTime.value();
  if (t==31) {
    sliderTime.value(1);
  } else if (t==30) {
    sliderTime.value(t+1);
    pause();
  } else {
    sliderTime.value(t+1);
  }
}
function play() {
  document.getElementById("play").disabled  = true;
  document.getElementById("pause").disabled = false;
  myTimer = setInterval(myCounter, 250);
}
function pause() {
  document.getElementById("play").disabled  = false;
  document.getElementById("pause").disabled = true;
  clearInterval(myTimer);
}
function reset() {
  document.getElementById("pause").disabled = true;
}