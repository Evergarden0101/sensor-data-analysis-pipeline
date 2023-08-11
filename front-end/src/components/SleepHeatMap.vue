<template>
    <h2 align="center">Sleep stage classification</h2>
    <p align="center">Every row represents a sleep cycle (90 minutes)</p>

    <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>

    <!--

    <div v-if="dataReceived">
        <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>
    </div>

    <div v-else>
        <el-row>
            <el-col :span="24" v-loading="loading" element-loading-text="The dataset is loading...it might take a couple of minutes.">
                <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>
            </el-col>
        </el-row>
    </div>
-->

</template>

<script>
import dataset from '../assets/1022102cFnorm.csv';
import * as echarts from 'echarts';
import axios from 'axios';
import { ref } from 'vue';

export default {
  name: 'SleepHeatMap',
  data () {
    return {
      data: dataset,
      ecgData: [],
      dataReceived: false,
      loading: ref(true),

    }
  },
  mounted() {
    this.drawTreatHeatMap(1, 1, 1222325);
  },
  methods: {
    getMax(arr, prop) {
        var max;
        for (var i=0 ; i<arr.length ; i++) {
            if (max == null || parseInt(arr[i][prop]) > parseInt(max[prop]))
                max = arr[i];
        }
        return max;
    },
    getEcgData(patient_id, week, night_id){
        const path = `http://localhost:5000/hrv-features/${patient_id}/${week}/${night_id}`
        const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };
        axios.get(path, {headers})
        .then((res) => {
            this.dataReceived = true;
            this.ecgData = res.data;

        })
        .catch(err=>{
            console.log(err)
        })

    },
    drawTreatHeatMap(patient_id, week, night_id){
        var dom = document.getElementById("chart-container");
        var myChart = echarts.init(dom, null, {
            renderer: "sgv",
            useDirtyRect: false
        });

        const path = `http://localhost:5000/hrv-features/${patient_id}/${week}/${night_id}`
        const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

        axios.get(path, {headers})
            .then((res) => {
            console.log("Data received");
            var option;

            var minutes = [5, 10 , 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90];
            var hours = ['1.5h', '3h', '4.5h',
                    '6h', '7.5h', '9h', '10.5h', '12h'];
            /*
            if(this.dataReceived===true){
            var data = this.ecgData; 
            }
            else{
                await this.getEcgData(1, 1, 1222325);
                data = this.ecgData;
            }
            */
            /*
            var data = [{'LF/HF': 2.0107152456813915,
                'SD': 290.6453341073007,
                'end_id': 300000,
                'stage': "nrem",
                'start_id': 0,
                'x': 0,
                'y': 0
            },
            {
                'LF/HF':1.2472080864024337,
                'SD': 172.26272979069515,
                'end_id': 600000,
                'stage': "rem",
                'start_id': 300000,
                'x': 1,
                'y': 0
            }, {
                'LF/HF':1.8449693678005492,
                'SD': 153.53789804010702,
                'end_id': 900000,
                'stage': "rem",
                'start_id': 600000,
                'x': 2,
                'y': 0
            }
            ];
            */

            var data = res.data.map(function (item) {
                return [item['x'], item['y'], item['SD'], item['stage']];
            });

            option = {
                tooltip: {
                    position: 'top'
                },
                animation: false,
                grid: {
                    height: '50%',
                    top: '10%'
                },
                xAxis: {
                    type: 'category',
                    name: 'minutes',
                    data: minutes,
                    splitArea: {
                        show: true
                    }
                },
                yAxis: {
                    type: 'category',
                    data: hours,
                    name: 'hours',
                    splitArea: {
                        show: true
                    }
                },
                visualMap: {
                    min: 0,
                    max: this.getMax(res.data, "SD").SD,
                    dimension: 2,
                    inRange : {   
                        color: ['#D3D3D3', '#009000'] //From smaller to bigger value ->
                    },
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '15%',
                },
                series: [{
                    name: 'Punch Card',
                    type: 'heatmap',
                    data: data,
                    label: {
                        show: true,
                        formatter: (param) => {
                            if (param.data[3]  === 'rem'){
                                return 'REM'
                            }
                            else{
                                return ''
                            }
                        
                        }
                    },
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            if (option && typeof option === "object") {
                myChart.setOption(option);
            }

            window.addEventListener("resize", myChart.resize);
        })
        .catch(err=>{
            console.log(err)
        })
    }
}
}
</script>