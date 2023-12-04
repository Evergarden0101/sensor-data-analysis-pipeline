<template>
    <h3 align="center">Weekly Events Detected for Patient</h3>
    <div id="chart-container" style="position: relative; height: 80vh;"></div>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';

export default {
  name: 'TreatHeatMap',
  data () {
    return {
      weeklyData: [],
    }
  },
  mounted() {
    this.getWeeklySummary();
    this.drawTreatHeatMap();
  },
  methods: {
    getWeeklySummary() {
        const path = `http://127.0.0.1:5000/weekly-summary/${this.$store.state.patientId}/${this.$store.state.week}/`;
        axios.get(path)
            .then((res) => {
              this.weeklyData = res.data;
              this.drawTreatHeatMap();
            })
            .catch(err => {
              console.log(err);
            });
    },
    drawTreatHeatMap(){
        var dom = document.getElementById("chart-container");
        var myChart = echarts.init(dom, null, {
            renderer: "sgv",
            useDirtyRect: false
        });
        // var app = {};

        // Determine the maximum cycle number from the data
        let maxCycle = this.weeklyData.reduce((max, item) => item.max_cycle > max ? item.max_cycle : max, 0);

        // Prepare the data for the heatmap
        let heatmapData = this.weeklyData.map(item => {
          return [item.day_no, item.cycle - 1, item.count];  // Adjust index if necessary
        });

        var option;
        const days = Array.from({length: 7}, (_, i) => i + 1);

        var callback = (args) => {
            if (args.value[2] === 1){
                return args.seriesName + "<br />" +args.marker + 'day '+parseInt(parseInt(args.value[0])+1) + ": " + args.value[2] + ' event'

            }
            else{
                return args.seriesName + "<br />" +args.marker + 'day '+parseInt(parseInt(args.value[0])+1) + ": " + args.value[2] + ' event(s)'
            }
        }

        option = {
            title:{
                text: ""
            },
            tooltip: {
                position: 'top',
                formatter: callback
            },
            grid: {
                height: '50%',
                top: '5%'
            },
            xAxis: {
                type: 'category',
                name: 'Day',
                data: days,
                splitArea: {
                    show: true
                },
            },
            yAxis: {
              type: 'category',
              name: 'Sleep Cycles',
              data: Array.from({ length: maxCycle }, (_, i) => i + 1),
              rotate: 30,
              splitArea: {
                show: true
              },
            },
            visualMap: {
                min: 0,
                max: 10,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '30%',
                text: ["max", "min"],
            },
            series: [
            {
                name: '<b>Details</b>',
                type: 'heatmap',
                data: heatmapData,
                label: {
                    show: true,
                },
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
            ]
        };

        if (option && typeof option === "object") {
            myChart.setOption(option);
        }

        window.addEventListener("resize", myChart.resize);

    }
  }
}
</script>