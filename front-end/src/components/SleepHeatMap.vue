<template>
    <h3 align="center">Sleep stage classification</h3>
    <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>
</template>

<script>
import dataset from '../assets/1022102cFnorm.csv'
import * as echarts from 'echarts';

export default {
  name: 'SleepHeatMap',
  data () {
    return {
      data: dataset,
    }
  },
  mounted() {
    this.drawTreatHeatMap();
  },
  methods: {
    drawTreatHeatMap(){
        var dom = document.getElementById("chart-container");
        var myChart = echarts.init(dom, null, {
            renderer: "sgv",
            useDirtyRect: false
        });
        // var app = {};

        var option;

        // prettier-ignore
        const hours = Array.from({length: 120}, (_, i) => i + 5);
        // prettier-ignore
        const night = Array.from({length: 1});
        // prettier-ignore
        const data = [[0, 0, 5]]
            .map(function (item) {
            return [item[0], item[1], item[2] || '-'];
        });
        option = {
            title:{
                text: "Night 1"
            },
            tooltip: {
                position: 'top'
            },
            grid: {
                height: '10%',
                top: '5%'
            },
            xAxis: {
                type: 'category',
                name: 'Sleep Time',
                data: hours,
                splitArea: {
                    show: true
                }
            },
            yAxis: {
                type: 'category',
                name: 'Night',
                data: night,
                splitArea: {
                    show: true
                },
                inverse: true,
            },
            visualMap: {
                min: 0,
                max: 10,
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '30%'
            },
            series: [
            {
                name: 'Punch Card',
                type: 'heatmap',
                data: data,
                label: {
                    show: true
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