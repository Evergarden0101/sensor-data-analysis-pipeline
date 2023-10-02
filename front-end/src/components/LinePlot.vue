<template>
    <!-- Initialize a select button -->
    <!-- <el-col :span="2"> -->
        <!-- <select id="selectButton"></select> -->
    <el-row style="width: 100%;">
        <h3 style="text-align: center;">Select your interested range from the plot.</h3>
    </el-row>
    <!-- </el-col> -->
    <!-- <el-col :span="22"> -->
    <el-row text-align="center" style="margin-bottom: 20px;width: 100%;">
        <el-checkbox v-model="checkedMR" label="Use Right Masseter for Classification" border @change="rerenderRight"/>
    </el-row>
    <el-row v-show="checkedMR" style="width: 100%;">
        <h4 style="margin-left: 40%;margin-bottom: 10px;">Sensor Signals for Right Masseter</h4>
    </el-row>
    <el-row style="margin-bottom: 40px;" v-show="checkedMR">
        <div id="mrlineplot" v-loading="loading" element-loading-text="The line plots are loading...it might take a couple of minutes."></div>
    </el-row>
    <!-- </el-col> -->
    <el-row text-align="center" style="margin-bottom: 20px;width: 100%;">
        <el-checkbox v-model="checkedML" label="Use Left Masseter for Classification" border @change="rerenderLeft"/>
    </el-row>
    <el-row v-show="checkedML" style="width: 100%;">
        <h4 style="margin-left: 40%;margin-bottom: 10px;">Sensor Signals for Left Masseter</h4>
    </el-row>
    <el-row v-show="checkedML" style="margin-bottom: 30px;">
        <div id="mllineplot" v-loading="loading" element-loading-text="The line plots are loading...it might take a couple of minutes."></div>
    </el-row>

</template>

<script>
import * as d3 from "d3";
import dataset from '../assets/1022102cFnorm copy.csv'
import axios from 'axios';
import { ref,computed } from 'vue'
import { style } from "plotly.js/lib/bar";
// import csvToJson from 'csvtojson';

export default {
    name: 'LinePlot',
    data () {
        return {
            data: null,
            checkedMR: this.$store.state.checkedMR,
            checkedML: this.$store.state.checkedML,
            freq: 2000,
            key: Date.now(),
            activeName: 'left',
            Labels: [],
            start: 0,
            end: 0,
            max: 10,
            error: false,
            remPhases: [],
            loading: true,
        }
    },
    async mounted() {
        this.Labels = this.loadAll();
        this.start = this.$store.state.plotStart;
        this.end = this.$store.state.plotEnd;
        // this.checkedML = this.$store.state.checkedML;
        // this.checkedMR = this.$store.state.checkedMR;
        this.data = dataset;
        if(this.data == null){
            await this.loadLinePlotData(this.$store.state.patientId, this.$store.state.week, this.$store.state.nightId);
            this.loading = false;
        }else{
            if(this.start == 0 && this.end == 0){
                this.end = (this.data.length-1)/this.freq;
            }
            this.$store.commit('updataPoint',{startPoint:this.start, endPoint:Math.floor(this.end * 1000) / 1000})
            if(this.checkedMR) await this.drawLineplot('MR',this.start,this.end);
            if(this.checkedML) await this.drawLineplot('ML',this.start,this.end);
            this.loading = false;
        }

    },
    methods: {
        loadAll() {
            return [
                {
                    'id': 'Label 1',
                    'Start': 5.952,
                    'End': 8.432,
                    // 'Dur': 2.48,
                    'Confirm': true,
                },
                {
                    'id': 'Label 2',
                    'Start': 9.868,
                    'End': 13.020,
                    // 'Dur': 3.162,
                    'Confirm': true,
                },
                {
                    'id': 'Label 3',
                    'Start': 15.634,
                    'End': 19.127,
                    // 'Dur': 3.4875,
                    'Confirm': true,
                },
                {
                  'id': 'Label 4',
                  'Start': 70.634,
                  'End': 81.127,
                  // 'Dur': 3.4875,
                  'Confirm': true,
                }
            ]
        },
        loadLinePlotData(patient_id, week, night_id){
            const path = `http://127.0.0.1:5000/lineplot-data/${patient_id}/${week}/${night_id}`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };

            axios.get(path, {headers})
                .then((res) => {
                    console.log("Data received");
                    // this.loading = ref(false);
                    console.log(res)
                    var option;
                    var maxY = 0;
                    var hours = [];

                    this.data = res.data;

                    if(this.start == 0 && this.end == 0){
                        this.end = (this.data.length-1)/this.freq;
                    }
                    this.$store.commit('updataPoint',{startPoint:this.start, endPoint:Math.floor(this.end * 1000) / 1000})
                    if(this.checkedMR) this.drawLineplot('MR',this.start,this.end);
                    if(this.checkedML) this.drawLineplot('ML',this.start,this.end);

                })
                .catch(err=>{
                    console.log(err)
                    this.error = true;
                })
        },
        rerenderLeft(tab,event) {
            if(tab == false){
                var ml = document.getElementById('mllineplot')
                this.emptyGraph(ml);
                this.$store.commit('selectML',false);
            } else if(tab == true){
                var start = this.$store.state.startPoint;
                var end = this.$store.state.endPoint;
                if (start == 0 && end == 0){
                    start = this.start;
                    end = this.end;
                }
                this.drawLineplot('ML', start, end);
                this.$store.commit('selectML',true);
            }
        },
        rerenderRight(tab,event) {
            if(tab == false){
                var mr = document.getElementById('mrlineplot')
                this.emptyGraph(mr);
                this.$store.commit('selectMR',false);
            } else if(tab == true){
                var start = this.$store.state.startPoint;
                var end = this.$store.state.endPoint;
                if (start == 0 && end == 0){
                    start = this.start;
                    end = this.end;
                }
                this.drawLineplot('MR', start, end);
                this.$store.commit('selectMR',true);
            }
        },
        emptyGraph(e) {
            while (e.firstChild) {
                console.log(e.firstChild)
                e.removeChild (e.firstChild);
            }
        },
        emptyLabelGraph(name) {
            let e = document.getElementById(name);
            console.log(e.children)
            let labels = e.getElementsByClassName("labels")
            while(labels!=null && labels.length!=0){
                e.removeChild (labels[0]);
                labels = e.getElementsByClassName("labels");
            }

            e = document.getElementById(name);
            console.log(e.children)

        },
        jsontoCsv(json){
            const jsonKeys = Object.keys(json[0]);
            const headerData = jsonKeys.join(',');
            const rowData = json.map((item) => {
                return jsonKeys.map((key) => item[key]).join(',');
                });
            const json2CSV = `${headerData}\n${rowData.join('\n')}`;
            return json2CSV;
        },
        csvToJson(csv) {

            console.log(csv)
            const lines = csv;
            const delimeter = ',';

            const result = [];

            const headers = String(lines[0]).split(delimeter);

            for (var i=1;i<lines.length;i++) {
                var line = lines[i];
                const obj = {};
                const row = String(line).split(delimeter);
                // console.log(row)

                for (let j = 0; j < headers.length-1; j++) {
                    const header = headers[j];
                    obj[header] = row[j];
                }
                obj['cnt'] = (i-1)/this.freq;

                result.push(obj);
            }

            // Prettify output
            return result;
        },
        drawLabel(channel, start, end){
            console.log('labels')
            var margin = {top: 10, right: 100, bottom: 40, left: 40};
            var height = document.body.clientHeight/4 - margin.top - margin.bottom;
            var width = document.body.clientWidth/2 - margin.left - margin.right;
            var x = d3.scaleLinear()
                // .domain(d3.extent(data, function(d) { return d.year; }))
                .domain([start, end])
                .range([ 0, width ]);

            var line = d3.select("#"+channel);
            var rects = line
                            .selectAll("rect")
                            .data(this.Labels)
                            .enter()
                            .append("rect")
                            // .datum(this.Labels)
                            .attr("x", (d=> x((d.Start))))
                            .attr("y", 0)
                            .attr("width", (d=> x(d.End) - x(d.Start)))
                            .attr("height", height)
                            .attr("fill", "teal")
                            .attr("opacity", 0.3)
                            .attr("class", "labels");
        },
        drawLineplot(channel,start, end){

            const remPhases = [
              {
                'id': 'REM Phase 1',
                'Start': 3.5,
                'End': 20
              },
              {
                'id': 'REM Phase 2',
                'Start': 70,
                'End': 100
              },
              // ... add more REM phases as needed
            ];

            var csv = this.csvToJson(this.data)

            // set the dimensions and margins of the graph
            var margin = {top: 10, right: 100, bottom: 40, left: 40},
                width = document.body.clientWidth/2 - margin.left - margin.right,
                height = document.body.clientHeight/4 - margin.top - margin.bottom;

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


            // Add X axis --> it is a date format
            var domainLen = (csv.length + 1)/this.freq;
            console.log(domainLen)
            var x = d3.scaleLinear()
                // .domain(d3.extent(data, function(d) { return d.year; }))
                .domain([start, end])
                .range([ 0, width ]);
            var xAxis = svg.append("g")
                .attr("transform", "translate(0," + height + ")")
                // .call(d3.axisBottom(x).ticks(5));
                .call(d3.axisBottom(x))
                .classed('axis_x', true)
                .attr("id", channel+'X');

            // Add Y axis
            var y = d3.scaleLinear()
                // .domain([0, d3.max(data, function(d) { return +d.n; })])
                .domain([-this.max, this.max])
                .range([ height, 0 ]);
            var yAxis = svg.append("g")
                .call(d3.axisLeft(y))
                .classed('axis_y', true)

            const highlightedEventsMR = [
            {start: 7},
            {start: 12},
            {start: 18},
            // {start: 27},
            ]

            const highlightedEventsML = [
            {start: 15}
            ]

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
                .attr("class", "line")
                .attr("fill", "none")
                .attr("stroke", "grey")
                .attr("stroke-width", 1.5)
                .attr("d", d3.line()
                    .x(function(d) { return x((d.cnt))})
                    .y(function(d) { return y(d[channel]) })
                );

            // Overlay colored line segments for the remPhases
            remPhases.forEach(phase => {
              // Calculate the data points within the remPhase range
              const phaseData = csv.filter(d => d.cnt >= phase.Start && d.cnt < phase.End);

              line.append("path")
                  .datum(phaseData)
                  .attr("class", "line")
                  .attr("fill", "none")
                  .attr("stroke", "url(#line-gradient)")
                  .attr("stroke-width", 1.5)
                  .attr("d", d3.line()
                      .x(function(d) { return x((d.cnt))})
                      .y(function(d) { return y(d[channel]) })
                  );
            });


            this.drawLabel(channel, start, end);

            // Add the brushing
            line
            .append("g")
                .attr("class", "brush")
                .call(brush);

            // A function that set idleTimeOut to null
            let idleTimeout
            function idled() { idleTimeout = null; }
            var store = this.$store;
            var that = this;
            // A function that update the chart for given boundaries
            function updateChart(event,d) {
                // What are the selected boundaries?
                var extent = event.selection

                // If no selection, back to initial coordinate. Otherwise, update X axis domain
                if(!extent){
                    if (!idleTimeout) return idleTimeout = setTimeout(idled, 350); // This allows to wait a little bit
                    x.domain([ 4,8])
                }else{
                    let sp = x.invert(extent[0]);
                    let ep = x.invert(extent[1]);
                    store.commit('updataPoint',
                        {startPoint:Math.floor(sp * 1000) / 1000, endPoint:Math.floor(ep * 1000) / 1000})

                    store.commit('setLabelRange',{plotStart:Math.floor(sp * 1000) / 1000, plotEnd:Math.floor(ep * 1000) / 1000});
                    store.commit('updateLinePlotKey');
                    x.domain([sp, ep]);

                    that.drawLabel('MR', sp, ep);
                    that.drawLabel('ML', sp, ep);
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
                    var otherX = d3.select("#MRX")
                    otherX.transition().duration(1000).call(d3.axisBottom(x))

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
                    var otherX = d3.select("#MLX")
                    otherX.transition().duration(1000).call(d3.axisBottom(x))

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
            var freq = this.freq;
            svg.on("dblclick",function(){
                let len = (csv.length)/freq;
                store.commit('updataPoint',{startPoint:0, endPoint:Math.floor(len * 1000) / 1000});
                store.commit('setLabelRange',{plotStart:0, plotEnd:0});

                store.commit('updateLinePlotKey');
            });

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
