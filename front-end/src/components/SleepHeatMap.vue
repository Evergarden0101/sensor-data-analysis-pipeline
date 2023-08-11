<template>
    <h2 align="center">Sleep stage classification</h2>
    <p align="center">Every row represents a sleep cycle (90 minutes)</p>

    <el-row>
        <el-col :span="24" v-loading="loading" element-loading-text="The dataset is loading...it might take a couple of minutes.">
            <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>
        </el-col>
    </el-row>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';
import { ref } from 'vue';

export default {
  name: 'SleepHeatMap',
  data () {
    return {
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
            this.loading = ref(false);
            var option;

            var minutes = [5, 10 , 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90];
            var hours = ['1.5h', '3h', '4.5h',
                    '6h', '7.5h', '9h', '10.5h', '12h'];
            
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
                        color: ['#F0FFFF', '#191970'] //From smaller to bigger value ->
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