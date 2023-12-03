<template>
    <el-row style="height:250px">
        <el-col :span="10" :offset="0" >
            <el-row style="height:102px;width:80%;left:10%">
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(STN*1.8)]}">
                                <h5 style="margin:0">TN</h5>
                                <h4>{{STN}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for TN</h4>
                            <div id="STN"></div>
                        </template>
                    </el-popover>
                </el-col>
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(SFP*1.8)]}">
                                <h5 style="margin:0">FP</h5>
                                <h4>{{SFP}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for FP</h4>
                            <div id="SFP"></div>
                        </template>
                    </el-popover>
                </el-col>
            </el-row>
            <el-row style="height:102px;width:80%;left:10%">
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid;" :style="{'background-color':color[Math.round(SFN*1.8)]}">
                                <h5 style="margin:0">FN</h5>
                                <h4>{{SFN}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for FN</h4>
                            <div id="SFN"></div>
                        </template>
                    </el-popover>
                </el-col>
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(STP*1.8)]}">
                                <h5 style="margin:0">TP</h5>
                                <h4>{{STP}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for TP</h4>
                            <div id="STP">    
                            </div>
                        </template>
                    </el-popover>
                </el-col>
            </el-row>
            <el-row style="text-align:center">
                <h4 style="display:block; margin: 10px auto; text-align:center"> Model Confusion Matrix for Cohert Study</h4>
            </el-row>
        </el-col>

        <el-col :span="10" :offset="0" >
            <el-row style="height:102px;width:80%;left:10%">
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(TN*1.8)]}">
                                <h5 style="margin:0">TN</h5>
                                <h4>{{TN}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for TN</h4>
                            <div id="TN"></div>
                        </template>
                    </el-popover>
                </el-col>
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(FP*1.8)]}">
                                <h5 style="margin:0">FP</h5>
                                <h4>{{FP}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for FP</h4>
                            <div id="FP"></div>
                        </template>
                    </el-popover>
                </el-col>
            </el-row>
            <el-row style="height:102px;width:80%;left:10%">
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid;" :style="{'background-color':color[Math.round(FN*1.8)]}">
                                <h5 style="margin:0">FN</h5>
                                <h4>{{FN}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for FN</h4>
                            <div id="FN"></div>
                        </template>
                    </el-popover>
                </el-col>
                <el-col :span="12" style="height:100px">
                    <el-popover trigger="click" :width="500" placement="right"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <el-card shadow="hover" style="margin:1px;height:100%;text-align:center;border:solid" :style="{'background-color':color[Math.round(TP*1.8)]}">
                                <h5 style="margin:0">TP</h5>
                                <h4>{{TP}}%</h4>
                            </el-card>
                        </template>
                        <template #default>
                            <h4 style="text-align:center">History plot for TP</h4>
                            <div id="TP">    
                            </div>
                        </template>
                    </el-popover>
                </el-col>
            </el-row>
            <el-row style="text-align:center">
                <h4 style="display:block; margin: 10px auto; text-align:center">Model Performance for Patient {{ this.$store.state.patientId }}</h4>
            </el-row>
        </el-col>

        <el-col :span="3" style="height:250px">
            <el-image style="height: 100%" :src="require('../assets/legend.png')" fit="contain" />
        </el-col>
    </el-row>
    
    <!-- <el-row style="height:300px;width:800px">
        <div id="general" style="position: relative; height: 300px;"></div>
    </el-row> -->
    <!-- <div id="legend"><canvas width="256" height="1" style="margin: 0px -14px; width: calc(100% + 28px); height: 33px; cursor: pointer;"></canvas></div> -->
</template>

<!-- Load d3.js -->

<script>
import * as d3 from "d3";
import axios from 'axios';
export default {
    name: 'ConfusionMatrix',
    data () {
        return {
            color: ["#ffffcc","#fffecb","#fffec9","#fffdc8","#fffdc6","#fffcc5","#fffcc4","#fffbc2","#fffac1","#fffac0","#fff9be","#fff9bd","#fff8bb","#fff8ba","#fff7b9","#fff6b7","#fff6b6","#fff5b5","#fff5b3","#fff4b2","#fff4b0","#fff3af","#fff2ae","#fff2ac","#fff1ab","#fff1aa","#fff0a8","#fff0a7","#ffefa6","#ffeea4","#ffeea3","#ffeda2","#ffeda0","#ffec9f","#ffeb9d","#ffeb9c","#ffea9b","#ffea99","#ffe998","#ffe897","#ffe895","#ffe794","#ffe693","#ffe691","#ffe590","#ffe48f","#ffe48d","#ffe38c","#fee28b","#fee289","#fee188","#fee087","#fee085","#fedf84","#fede83","#fedd82","#fedc80","#fedc7f","#fedb7e","#feda7c","#fed97b","#fed87a","#fed778","#fed777","#fed676","#fed574","#fed473","#fed372","#fed270","#fed16f","#fed06e","#fecf6c","#fece6b","#fecd6a","#fecb69","#feca67","#fec966","#fec865","#fec764","#fec662","#fec561","#fec460","#fec25f","#fec15e","#fec05c","#febf5b","#febe5a","#febd59","#febb58","#feba57","#feb956","#feb855","#feb754","#feb553","#feb452","#feb351","#feb250","#feb14f","#feb04e","#feae4d","#fead4d","#feac4c","#feab4b","#feaa4a","#fea84a","#fea749","#fea648","#fea547","#fea347","#fea246","#fea145","#fda045","#fd9e44","#fd9d44","#fd9c43","#fd9b42","#fd9942","#fd9841","#fd9741","#fd9540","#fd9440","#fd923f","#fd913f","#fd8f3e","#fd8e3e","#fd8d3d","#fd8b3c","#fd893c","#fd883b","#fd863b","#fd853a","#fd833a","#fd8139","#fd8039","#fd7e38","#fd7c38","#fd7b37","#fd7937","#fd7736","#fc7535","#fc7335","#fc7234","#fc7034","#fc6e33","#fc6c33","#fc6a32","#fc6832","#fb6731","#fb6531","#fb6330","#fb6130","#fb5f2f","#fa5d2e","#fa5c2e","#fa5a2d","#fa582d","#f9562c","#f9542c","#f9522b","#f8512b","#f84f2a","#f74d2a","#f74b29","#f64929","#f64828","#f54628","#f54427","#f44227","#f44127","#f33f26","#f23d26","#f23c25","#f13a25","#f03824","#f03724","#ef3524","#ee3423","#ed3223","#ed3123","#ec2f22","#eb2e22","#ea2c22","#e92b22","#e92921","#e82821","#e72621","#e62521","#e52420","#e42220","#e32120","#e22020","#e11f20","#e01d20","#df1c20","#de1b20","#dd1a20","#dc1920","#db1820","#da1720","#d91620","#d81520","#d71420","#d51320","#d41221","#d31121","#d21021","#d10f21","#cf0e21","#ce0d21","#cd0d22","#cc0c22","#ca0b22","#c90a22","#c80a22","#c60923","#c50823","#c40823","#c20723","#c10723","#bf0624","#be0624","#bc0524","#bb0524","#b90424","#b80424","#b60425","#b50325","#b30325","#b10325","#b00225","#ae0225","#ac0225","#ab0225","#a90125","#a70126","#a50126","#a40126","#a20126","#a00126","#9e0126","#9c0026","#9a0026","#990026","#970026","#950026","#930026","#910026","#8f0026","#8d0026","#8b0026","#8a0026","#880026","#860026","#840026","#820026","#800026"],
            FN: 11.22,
            FP: 22.53,
            TN: 88.78,
            TP: 77.47,
            SFN: 10.76,
            SFP: 29.13,
            STN: 89.24,
            STP: 70.87,
            accuracies: [{'id': 0, 'TP':68.32, 'FN':23.84, 'FP': 31.68, 'TN': 76.16}, {'id': 1, 'TP':77.47, 'FN': 11.22, 'FP': 22.53, 'TN': 88.78}],
            saccuaracies: [{'id': 0, 'TP':68.32, 'FN':23.84, 'FP': 31.68, 'TN': 76.16}, {'id': 1, 'TP':77.47, 'FN': 11.22, 'FP': 22.53, 'TN': 88.78}],
        }
    },
    beforeMount() {
        this.getPrecision();
    },
    mounted() {
        this.drawConfusionMatrix('FN', true);
        this.drawConfusionMatrix('FP', true);
        this.drawConfusionMatrix('TN', true);
        this.drawConfusionMatrix('TP', true);
        this.drawConfusionMatrix('FN', false);
        this.drawConfusionMatrix('FP', false);
        this.drawConfusionMatrix('TN', false);
        this.drawConfusionMatrix('TP', false);
        // this.drawLegend()
        // this.drawConfusionMatrix('general');
    },
    methods: {
        getPrecision(){

        },
        drawLegend(){
            const colors = d3[`scheme${YlOrRd}`];
            // const n = colors.length;
            const n = 180;
            const dark = d3.lab(colors[0]).l < 50;;
            const canvas = svg`<svg viewBox="0 0 ${n} 1" style="display:block;width:${n * 33}px;height:33px;margin:0 -14px;cursor:pointer;">${colors.map((c, i) => svg`<rect x=${i} width=1 height=1 fill=${c}>`)}`;
            const label = document.getElementById('legend');
            label.textContent = name;
            label.style.position = "absolute";
            label.style.top = "4px";
            label.style.color = dark ? `#fff` : `#000`;
        },
        drawConfusionMatrix(type, study){
            console.log("draw Confusion Matrix");
            // set the dimensions and margins of the graph
            if(study){
                var name = 'S'+type;
                var data = this.saccuaracies;
            } else {
                var name = type;
                var data = this.accuracies;
            }
            const margin = {top: 10, right: 30, bottom: 35, left: 60},
                width = 460 - margin.left - margin.right,
                height = 300 - margin.top - margin.bottom;

            // append the svg object to the body of the page
            const svg = d3.select('#'+name)
            .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
            .append("g")
                .attr("transform",`translate(${margin.left},${margin.top})`);

            //Read the data
            // var data = this.accuracies;

            // d3.csv("https://raw.githubusercontent.com/holtzy/D3-graph-gallery/master/DATA/connectedscatter.csv",

            // // When reading the csv, I must format variables:
            // d => {
            //     return {date : d3.timeParse("%Y-%m-%d")(d.date), value : d.value}}).then(

            // Now I can use this dataset:
            // function(data) {
            console.log('data: ', data);

            // Add X axis --> it is a date format
            const x = d3.scaleOrdinal()
            .domain(d3.extent(data, d => d.id+1))
            .range([ 0, width ]);
            svg.append("g")
            .attr("transform", `translate(0, ${height})`)
            .call(d3.axisBottom(x));

            // Add Y axis
            const y = d3.scaleLinear()
            .domain( [0, 100])
            .range([ height, 0 ]);
            svg.append("g")
            .call(d3.axisLeft(y));

            // Add X axis label:
            svg.append("text")
                .attr("text-anchor", "end")
                .attr("x", width)
                .attr("y", height + 35)
                .attr("style","font-size: 13px")
                .text("Iteration");

            // Add Y axis label:
            svg.append("text")
                .attr("text-anchor", "end")
                .attr("y", 6)
                .attr("dy", "-3.5em")
                .attr("transform", "rotate(-90)")
                .attr("style","font-size: 13px")
                .text("Percentage")

            // Add the line
            svg.append("path")
            .datum(data)
            .attr("fill", "none")
            .attr("stroke", "black")
            .attr("stroke-width", 1.5)
            .attr("d", d3.line()
                .curve(d3.curveBasis) // Just add that to have a curve instead of segments
                .x(d => x(d.id+1))
                .y(d => y(d[type]))
                )

            // create a tooltip
            const Tooltip = d3.select('#'+name)
            .append("div")
            .style("opacity", 0)
            .attr("class", "tooltip")
            .style("background-color", "white")
            .style("border", "solid")
            .style("border-width", "2px")
            .style("border-radius", "5px")
            .style("padding", "5px")

            // Three function that change the tooltip when user hover / move / leave a cell
            const mouseover = function(event,d) {
                Tooltip
                .style("opacity", 1)
            }
            const mousemove = function(event,d) {
                Tooltip
                .html("Recorded Value: " + d[type])
                .style("left", `${event.layerX+10}px`)
                .style("top", `${event.layerY}px`)
            }
            const mouseleave = function(event,d) {
                Tooltip
                .style("opacity", 0)
            }



            // Add the points
            svg
            .append("g")
            .selectAll("dot")
            .data(data)
            .join("circle")
                .attr("class", "myCircle")
                .attr("cx", d => x(d.id+1))
                .attr("cy", d => y(d[type]))
                .attr("r", 8)
                .attr("stroke", "#69b3a2")
                .attr("stroke-width", 3)
                .attr("fill", "white")
                .on("mouseover", mouseover)
                .on("mousemove", mousemove)
                .on("mouseleave", mouseleave)
            // }
            
        }
    },
}
</script>