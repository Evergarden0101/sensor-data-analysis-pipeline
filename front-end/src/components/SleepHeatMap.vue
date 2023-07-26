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

        var option;

        var minutes = [5, 10 , 15, 20, 25, 30, 35, 40, 45, 50, 55, 60];
        var hours = ['1h', '2h', '3h',
                '4h', '5h', '6h', '7h', '8h', '9h'];

        var data = [[0,0,4.53, 'R'],[0,1, 7, 'NR'], [0,2, 0, 'R']];

        data = data.map(function (item) {
            return [item[1], item[0], item[2]];
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
                data: minutes,
                splitArea: {
                    show: true
                }
            },
            yAxis: {
                type: 'category',
                data: hours,
                splitArea: {
                    show: true
                }
            },
            visualMap: {
                min: 0,
                max: 10,
                inRange : {   
                    color: ['#D3D3D3', '#009000' ] //From smaller to bigger value ->
                },
                calculable: true,
                orient: 'horizontal',
                left: 'center',
                bottom: '15%'
            },
            series: [{
                name: 'Punch Card',
                type: 'heatmap',
                data: data,
                label: {
                    normal: {
                        show: true,
                        formatter: () => {
                            if (data[3] ===  'R') {
                                return 'REM';
                            }
                            if (data[3] ===  'NR') {
                                return 'NREM';
                            }
                        
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
    }
}
}
</script>