<template>
    <!-- Initialize a select button -->
    <!-- <el-col :span="2"> -->
        <!-- <select id="selectButton"></select> -->
    <el-row style="width: 100%;">
        <h3 style="text-align: center;">Pick the labels from the plot.</h3>
    </el-row>
    <!-- </el-col> -->
    <!-- <el-col :span="22"> -->
    <el-row text-align="center" style="margin-bottom: 20px;width: 100%;">
        <el-checkbox v-model="checkedMR" label="Use Right Masseter for Classification" border @change="rerender"/>
    </el-row>
    <el-row v-show="checkedMR" style="width: 100%;">
        <h4 style="margin-left: 40%;margin-bottom: 10px;">Sensor Signals for Right Masseter</h4>
    </el-row>
    <el-row style="margin-bottom: 40px;" v-show="checkedMR">
        <div id="mrlineplot" ></div>
    </el-row>
    <!-- </el-col> -->
    <el-row text-align="center" style="margin-bottom: 20px;width: 100%;">
        <el-checkbox v-model="checkedML" label="Use Left Masseter for Classification" border @change="rerender"/>
    </el-row>
    <el-row v-show="checkedML" style="width: 100%;">
        <h4 style="margin-left: 40%;margin-bottom: 10px;">Sensor Signals for Left Masseter</h4>
    </el-row>
    <el-row v-show="checkedML" style="margin-bottom: 30px;">
        <div id="mllineplot" ></div>
    </el-row>

</template>

<script>
import * as d3 from "d3";
import dataset from '../assets/1022102cFnorm.csv'
import { ref } from 'vue'
import { style } from "plotly.js/lib/bar";
// import csvToJson from 'csvtojson';

export default {
  name: 'LinePlot',
  data () {
    return {
        data: dataset,
        checkedMR: ref(true),
        checkedML: ref(true),
        freq: 2000,
        key: Date.now(),
    }
  },
  mounted() {
        this.drawLineplot('MR');
        this.drawLineplot('ML');
  },
  methods: {
    rerender() {
        this.key = Date.now();
    },
    csvToJson(csv) {
        // \n or \r\n depending on the EOL sequence
        // const lines = csv.split('\n');
        const lines = csv;
        const delimeter = ',';

        const result = [];

        const headers = String(lines[0]).split(delimeter);

        for (var i=1;i<lines.length;i++) {
            var line = lines[i];
            const obj = {};
            const row = String(line).split(delimeter);

            for (let i = 0; i < headers.length-1; i++) {
                const header = headers[i];
                obj[header] = row[i];
            }
            obj['cnt'] = (i-1)/this.freq;

            result.push(obj);
        }

        // Prettify output
        return result;
    },

    drawLineplot(channel){
        // const csvFilePath = '@/assets/1022102cFnorm.csv';
        // var csv = await csvToJson().fromFile(csvFilePath);
        var csv = this.csvToJson(dataset)
        // const csvs = JSON.stringify(csv, null, 2);
        // this.data = csvs;

        // set the dimensions and margins of the graph
        var margin = {top: 10, right: 100, bottom: 40, left: 40},
            width = 850 - margin.left - margin.right,
            height = 300 - margin.top - margin.bottom;

        // append the svg object to the body of the page
        if(channel == 'MR'){
            var svg = d3.select("#mrlineplot")
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");
        } else if(channel == 'ML'){
            var svg = d3.select("#mllineplot")
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",
                    "translate(" + margin.left + "," + margin.top + ")");
        }

        // group the data: I want to draw one line per group
        // var sumstat = d3.group() // nest function allows to group the calculation per level of a factor
        //     .key(function(d) { return d.key;})
        //     .entries(data);


        // add the options to the button
        // var allGroup = String(this.data[0]).split(',');
        // d3.select("#selectButton")
        // .selectAll('myOptions')
        //     .data(allGroup)
        // .enter()
        //     .append('option')
        // .text(function (d) { return d; }) // text showed in the menu
        // .attr("value", function (d) { return d; }) // corresponding value returned by the button

        // A color scale: one color for each group
        // var myColor = d3.scaleOrdinal()
        //     .domain(allGroup)
        //     .range(d3.schemeSet2);


        // Add X axis --> it is a date format
        var x = d3.scaleLinear()
            // .domain(d3.extent(data, function(d) { return d.year; }))
            .domain([0, (csv.length + 1)/this.freq])
            .range([ 0, width ]);
        var xAxis = svg.append("g")
            .attr("transform", "translate(0," + height + ")")
            // .call(d3.axisBottom(x).ticks(5));
            .call(d3.axisBottom(x))
            .classed('axis_x', true);

        var max = 10;
        // Add Y axis
        var y = d3.scaleLinear()
            // .domain([0, d3.max(data, function(d) { return +d.n; })])
            .domain([-10, max])
            .range([ height, 0 ]);
        var yAxis = svg.append("g")
            .call(d3.axisLeft(y))
            .classed('axis_y', true)

        // Add X axis label:
        svg.append("text")
            .attr("text-anchor", "end")
            .attr("x", width)
            .attr("y", height + 35)
            .attr("style","font-size: 13px")
            .text("Time (s)");

        // Add Y axis label:
        svg.append("text")
            .attr("text-anchor", "end")
            .attr("y", 6)
            .attr("dy", "-2.5em")
            .attr("transform", "rotate(-90)")
            .attr("style","font-size: 13px")
            .text("Amplitude (mV)")
            // .attr("text-anchor", "start")

        // color palette
        // var res = sumstat.map(function(d){ return d.key }) // list of group names
        var res = this.data[0];
        var color = d3.scaleOrdinal()
            .domain(res)
            .range(['#e41a1c','#377eb8','#4daf4a','#984ea3','#ff7f00','#ffff33','#a65628'])
            // ,'#f781bf','#999999'])

        // Draw the line
        // svg.selectAll(".line")
        //     .data(this.data)
        //     .enter()
        //     .append("path")
        //         .attr("fill", "none")
        //         .attr("stroke", function(d){ return color(d.key) })
        //         .attr("stroke-width", 1.5)
        //         .attr("d", function(d){
        //         return d3.line()
        //             .x(function(d) { return x(range([0,d.length+1])); })
        //             .y(function(d) { return y(d.MR); })
        //             (d.values)
        //         })

        // Add a clipPath: everything out of this area won't be drawn.
        const clip = svg.append("defs").append("svg:clipPath")
            .attr("id", "clip")
            .append("svg:rect")
            .attr("width", width )
            .attr("height", height )
            .attr("x", 0)
            .attr("y", 0);

        // Add brushing
        const brush = d3.brushX()                   // Add the brush feature using the d3.brush function
            .extent( [ [0,0], [width,height] ] )  // initialise the brush area: start at 0,0 and finishes at width,height: it means I select the whole graph area
            .on("end", updateChart)               // Each time the brush selection changes, trigger the 'updateChart' function


        // Create the line variable: where both the line and the brush take place
        const line = svg.append('g')
            .attr("clip-path", "url(#clip)")
            .attr("id", channel)

        // Set the gradient
        svg.append("linearGradient")
        .attr("id", "line-gradient")
        .attr("gradientUnits", "userSpaceOnUse")
        .attr("x1", 0)
        .attr("y1", y(0))
        .attr("x2", 0)
        .attr("y2", y(2))
        .selectAll("stop")
            .data([
            {offset: "0%", color: "blue"},
            {offset: "100%", color: "red"}
            ])
        .enter().append("stop")
            .attr("offset", function(d) { return d.offset; })
            .attr("stop-color", function(d) { return d.color; });

        line.append("path")
            .datum(csv)
            .attr("class", "line")  // I add the class line to be able to modify this line later on.
            .attr("fill", "none")
            .attr("stroke", "url(#line-gradient)" )
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
                .x(function(d) { return x((d.cnt))})
                .y(function(d) { return y(d[channel]) })
            )
            // .attr("stroke", function(d){ return myColor("MR") })

        // Add the brushing
        line
        .append("g")
            .attr("class", "brush")
            .call(brush);

        // A function that set idleTimeOut to null
        let idleTimeout
        function idled() { idleTimeout = null; }

        // A function that update the chart for given boundaries
        function updateChart(event,d) {
            // What are the selected boundaries?
            var extent = event.selection

            // If no selection, back to initial coordinate. Otherwise, update X axis domain
            if(!extent){
                if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
                x.domain([ 4,8])
            }else{
                x.domain([ x.invert(extent[0]), x.invert(extent[1])])
                line.select(".brush").call(brush.move, null) // This remove the grey brush area as soon as the selection has been done
            }

            // Update axis and line position
            xAxis.transition().duration(1000).call(d3.axisBottom(x))

            line
                .select('.line')
                .transition()
                .duration(1000)
                .attr("d", d3.line()
                    .x(function(d) { return x(d.cnt)})
                    .y(function(d) { return y(d[channel]) })
                )


            if(channel == 'ML'){
                var otherLine = d3.select("#MR")
                otherLine.select('.line')
                .transition()
                .duration(1000)
                .attr("d", d3.line()
                    .x(function(d) { return x(d.cnt)})
                    .y(function(d) { return y(d.MR)})
                )
            }
            else if(channel == 'MR'){
                var otherLine = d3.select("#ML")
                otherLine.select('.line')
                .transition()
                .duration(1000)
                .attr("d", d3.line()
                    .x(function(d) { return x(d.cnt)})
                    .y(function(d) { return y(d.ML)})
                )
            }


        }

        // If user double click, reinitialize the chart
        svg.on("dblclick",function(){
            x.domain([0, csv.length + 1])
            xAxis.transition().call(d3.axisBottom(x))
            line
                .select('.line')
                .transition()
                .attr("d", d3.line()
                .x(function(d) { return x(d.cnt)})
                .y(function(d) { return y(d[channel]) })
            )

            if(channel == 'ML'){
                var otherLine = d3.select("#MR")
                otherLine.select('.line')
                .transition()
                .attr("d", d3.line()
                .x(function(d) { return x(d.cnt)})
                .y(function(d) { return y(d.MR)}))
            }
            else if(channel == 'MR'){
                var otherLine = d3.select("#ML")
                otherLine.select('.line')
                .transition()
                .attr("d", d3.line()
                .x(function(d) { return x(d.cnt)})
                .y(function(d) { return y(d.ML)}))
            }
        });

        // A function that update the chart
        // function update(selectedGroup) {
        //     // Create new data with the selection?
        //     var dataFilter = csv.map(function(d){return {cnt: d.cnt, value:d[selectedGroup]} })
        //     console.log(selectedGroup)
        //     console.log(dataFilter)
        //     // Give these new data to update line
        //     line
        //         .datum(dataFilter)
        //         .transition()
        //         .duration(1000)
        //         .attr("d", d3.line()
        //         .x(function(d) { return x(d.cnt) })
        //         .y(function(d) { return y(+d.value) })
        //         )
        //         // .attr("stroke", function(d){ return myColor(selectedGroup) })
        // }

        // When the button is changed, run the updateChart function
        // d3.select("#selectButton").on("change", function(d) {
        //     // recover the option that has been chosen
        //     var selectedOption = d3.select(this).property("value")
        //     // run the updateChart function with this selected option
        //     update(selectedOption)
        // })
    }
  },
}
</script>
<style scoped>
.el-row{
    display:flex;
    flex-wrap: wrap;
}
</style>
