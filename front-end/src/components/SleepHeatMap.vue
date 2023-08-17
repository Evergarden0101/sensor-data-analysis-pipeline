<template>
    <h2 align="center">Sleep Stage Classification</h2>
    <p align="center">Every row represents a sleep cycle (90 minutes).</p>
    <p align="center">The color bars represent the level of uncertainity.
        <el-tooltip placement="top" effect="light">
            <template #content>The level of uncertainity is derived from the Standard deviation of the LF/HF measure of the Heart Rate Variability (HRV) analyis. <br /> The ranges to classify the different sleep stages were taken from the following study: <br /><a href="https://www.frontiersin.org/articles/10.3389/fphys.2017.01100/full">Herzig, David, et al. "Reproducibility of heart rate variability is parameter and sleep stage dependent." Frontiers in physiology 8 (2018): 1100.</a> </template>
            <el-button size="small" circle ><el-icon><InfoFilled /></el-icon></el-button>
        </el-tooltip>
    </p>

    <el-row style="margin-top: 3%;">
        <el-col :span="7" :offset="5">
            <router-link :to="'/patient/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Patient Information</el-button>
            </router-link>
        </el-col>
        <el-col :span="7" :offset="5">
            <router-link :to="'/bruxism/'">
                <el-button type="primary" plain>
                    Bruxism Detection<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
            </router-link>
        </el-col>
    </el-row>

  <div class="buttons-container">
    <el-button @click="toggleEditMode" v-if="!isEditMode">Enter Edit Mode</el-button>
    <el-button @click="toggleEditMode" v-if="isEditMode">Exit Edit Mode</el-button>
    <el-button @click="toggleSelectMode">Select</el-button>
  </div>

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
import { h } from 'vue';
import { ElMessage } from 'element-plus';

export default {
  name: 'SleepHeatMap',
  data () {
    return {
      dataReceived: false,
      loading: ref(true),
      isEditMode: false,
      isSelectMode: false,
      selectedTiles: [],
      selectedIndices: []

    }
  },
  mounted() {
    this.drawTreatHeatMap(1, 1, 1222325);
  },
  methods: {
    open() {
        ElMessage('Please choose the cell for which you want to modify the label.')
    },
    getMax(arr, prop) {
        var max;
        for (var i=0 ; i<arr.length ; i++) {
            if (max == null || parseInt(arr[i][prop]) > parseInt(max[prop]))
                max = arr[i];
        }
        return max;
    },
    getMin(arr, prop) {
        var min;
        for (var i=0 ; i<arr.length ; i++) {
            if (min == null || parseInt(arr[i][prop]) < parseInt(min[prop]))
                min = arr[i];
        }
        return min;
    },
    toggleEditMode() {
      this.isEditMode = !this.isEditMode;
    },

    toggleSelectMode() {
      this.isSelectMode = !this.isSelectMode;

      // Ensure that you can't be in both edit and select mode simultaneously
      if (!this.isSelectMode) {
        this.isEditMode = false;
      }
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
                    '6h', '7.5h', '9h', '10.5h'];

            var remDataJson = []
            var nremDataJson = []
            for (var i=0; i < res.data.length; i++) {
                if(res.data[i]['stage'] === 'rem'){
                    remDataJson.push(res.data[i]);
                }
                else {
                    nremDataJson.push(res.data[i]);
                }
            }

            var remData = remDataJson.map(function (item) {
                return [item['x'], item['y'], parseInt(item['SD']), item['stage'], item['LF_HF']];
            });

            var nremData = nremDataJson.map(function (item) {
                return [item['x'], item['y'], parseInt(item['SD']), item['stage'], item['LF_HF']];
            });

            var callback = (args) => {
                return args.seriesName + "<br />" +args.marker  + args.value[4].toFixed(2) + '±' + args.value[2]
            }

            option = {
                tooltip: {
                    position: 'top',
                    formatter: callback
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
                visualMap: [{
                    min: this.getMin(remDataJson, "SD").SD,
                    max: this.getMax(remDataJson, "SD").SD,
                    dimension: 2,
                    inRange : {
                        color: ['#1919ff', '#CCCCFF'] //From bigger to smaller value ->
                    },
                    seriesIndex : 0,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '30%',
                }, {
                    min: this.getMin(nremDataJson, "SD").SD,
                    max: this.getMax(nremDataJson, "SD").SD,
                    dimension: 2,
                    inRange : {
                        color: ['#999999', '#eeeeee'] //From bigger to smaller value ->
                    },
                    seriesIndex : 1,
                    calculable: true,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '24%',
                }],
                series: [{
                    name: '<b>LF/HF ratio ± Standard Deviation (SD)</b>',
                    type: 'heatmap',
                    data: remData,
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
                            shadowColor: 'rgba(0, 0, 0, 0.5)',
                            borderColor: 'black'
                        }
                    }
                }, {
                    name: '<b>LF/HF ratio ± Standard Deviation (SD)</b>',
                    type: 'heatmap',
                    data: nremData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };

            myChart.on('click', (params) => {
              console.log('Tile clicked:', params);

              if (this.isEditMode) {
                if (params.seriesIndex === 0) { // If the clicked series is 'rem'
                  // Remove from 'rem' dataset
                  let removedData = option.series[0].data.splice(params.dataIndex, 1)[0];

                  // Modify the stage value
                  removedData[3] = 'nrem';

                  // Add to 'nrem' dataset
                  option.series[1].data.push(removedData);

                } else if (params.seriesIndex === 1) { // If the clicked series is 'nrem'
                  // Remove from 'nrem' dataset
                  let removedData = option.series[1].data.splice(params.dataIndex, 1)[0];

                  // Modify the stage value
                  removedData[3] = 'rem';

                  // Add to 'rem' dataset
                  option.series[0].data.push(removedData);
                }

                // Update the chart with the modified options
                myChart.setOption(option);
              }

              else if (this.isSelectMode) {
                console.log('Select mode is active');
                let dataIndex = `${params.seriesIndex}-${params.dataIndex}`;
                console.log('Selected Indices:', this.selectedIndices);

                if (this.selectedIndices.includes(dataIndex)) {
                  // If already selected, remove from the selectedIndices array
                  this.selectedIndices = this.selectedIndices.filter(i => i !== dataIndex);

                  // De-emphasize
                  myChart.dispatchAction({
                    type: 'downplay',
                    seriesIndex: params.seriesIndex,
                    dataIndex: params.dataIndex
                  });
                } else {
                  // Otherwise, add to the selectedIndices array
                  this.selectedIndices.push(dataIndex);

                  // Emphasize
                  myChart.dispatchAction({
                    type: 'highlight',
                    seriesIndex: params.seriesIndex,
                    dataIndex: params.dataIndex
                  });
                }
              }
            });

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

<style scoped>
.buttons-container {
  position: absolute;
  top: 175px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 10px;
}
</style>
