<template>
    <h2 align="center">Patient: {{ this.$store.state.patientId }}, Week: {{ this.$store.state.week }}, Night id: {{ this.$store.state.nightId }}</h2>
    <h3 align="center">Threshold Filtering</h3>
    <p align="center">Every row represents a sleep cycle (90 minutes).</p>
    <p align="center">The color bars represent the level of uncertainity.
        <el-tooltip placement="top" effect="light">
            <template #content>The level of uncertainity is derived from the Standard deviation of the LF/HF measure of the Heart Rate Variability (HRV) analyis. <br /> The ranges to classify the different sleep stages were taken from the following study: <br /><a href="https://www.frontiersin.org/articles/10.3389/fphys.2017.01100/full">Herzig, David, et al. "Reproducibility of heart rate variability is parameter and sleep stage dependent." Frontiers in physiology 8 (2018): 1100.</a> </template>
            <el-button size="small" circle ><el-icon><InfoFilled /></el-icon></el-button>
        </el-tooltip>
    </p>

    <el-row style="margin-top: 3%;">
        <el-col :span="7" :offset="5">
            <router-link :to="'/patient-data/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Patient Information</el-button>
            </router-link>
        </el-col>
        <el-col :span="7" :offset="5">
            <router-link :to="'/bruxism/'">
                <el-button v-if="!error" type="primary" plain>
                    Events Detection<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
            </router-link>
        </el-col>
    </el-row>

  <div v-if="!error" class="buttons-container">
    <el-button @click="toggleEditMode" v-if="!isEditMode">Enter Edit Mode</el-button>
    <el-popconfirm
    title="Are you sure you want to exit the edit mode?
    This will update the values forever."
    @confirm="toggleEditModeAndSelect"
    @cancel="exitEditMode"
    width="350">
        <template #reference>
            <el-button v-if="isEditMode">Exit Edit Mode</el-button>
        </template>
    </el-popconfirm>
<!--    <el-button @click="toggleSelectMode">Select</el-button>-->
  </div>

  <el-row>
        <el-col v-if="error" :span="24">
            <el-result
                icon="error"
                title="Error"
            >
                <template #extra>
                    <p>{{ getSubtitle() }}</p>
                    <router-link :to="'/patient-data/'">
                        <el-button type="primary" plain>Back</el-button>
                    </router-link>
                </template>
            </el-result>
        </el-col>
        <el-col v-if="!error" :span="24" v-loading="loading" element-loading-text="The dataset is loading...it might take a couple of minutes.">
            <div id="chart-container" style="position: relative; height: 80vh; overflow: hidden;"></div>
        </el-col>
    </el-row>
</template>

<script>
import * as echarts from 'echarts';
import axios from 'axios';
import { ref } from 'vue';
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
      selectedIndices: [],
      error: false,
      toUpdate: []
    }
  },
  mounted() {
    this.drawTreatHeatMap(this.$store.state.patientId, this.$store.state.week, this.$store.state.nightId);
  },
  methods: {
    open() {
        ElMessage('Please choose the cell for which you want to modify the label.')
    },
    getSubtitle(){
        return "No dataset found for user " + this.$store.state.patientId + " on night " + this.$store.state.nightId + " of week " + this.$store.state.week + "."
    },
    getMaxSD(arr, prop) {
        var max;
        if(arr.length === 0){
            return 0;
        }
        else{
            for (var i=0 ; i<arr.length ; i++) {
                if (max == null || parseInt(arr[i][prop]) > parseInt(max[prop]))
                    max = arr[i];
            }
            return max.SD;
        }

        
    },
    getMinSD(arr, prop) {
        var min;
        if(arr.length === 0){
            return 0;
        }
        else{
           for (var i=0 ; i<arr.length ; i++) {
            if (min == null || parseInt(arr[i][prop]) < parseInt(min[prop]))
                min = arr[i];
            }
            return min.SD; 
        }

        
    },

    toggleEditModeAndSelect() {
      this.toggleEditMode(); // Toggle off the edit mode
      this.toggleSelectMode(); // Toggle on the select mode
    },

    toggleEditMode() {
      this.isEditMode = !this.isEditMode;
      if(!this.isEditMode){
        const path = `http://localhost:5000/ssd/${this.$store.state.patientId}/${this.$store.state.week}/${this.$store.state.nightId}`
        const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
        };
        const payload = this.toUpdate;
        axios.post(path, payload, {headers})
            .then((res) => {
                console.log(res);
                this.toUpdate = [];
            })
            .catch(err=>{
                console.log(err)
            })

      }

    },
    exitEditMode(){
        this.isEditMode = !this.isEditMode;
        this.toUpdate = [];
        this.$router.go();
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

        const path = `http://localhost:5000/ssd/${patient_id}/${week}/${night_id}`
        const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
        };

        axios.get(path, {headers})
            .then((res) => {
            console.log("Data received");
            this.loading = ref(false);
            var option;
            var maxY = 0;
            var hours = [];
            var minutes = [5, 10 , 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90];
            var remDataJson = []
            var nremDataJson = []
            this.patientData = res.data;

            for (var i=0; i < res.data.length; i++) {
                if(res.data[i]['y'] > maxY){
                    maxY = res.data[i]['y']
                }
                if(res.data[i]['stage'] === 'rem'){
                    remDataJson.push(res.data[i]);
                }
                else {
                    nremDataJson.push(res.data[i]);
                }
            }

            for(var i=1.5; i<=(maxY+1)*1.5; i+=1.5){
                hours.push(i);
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
                    axisLabel: {
                        padding: [0, -60, 0, 0]
                    },
                    position: 'right',
                    type: 'category',
                    name: 'minutes',
                    data: minutes,
                    splitArea: {
                        show: true
                    },
                },
                yAxis: {
                    axisLabel: {
                        //why padding not working for 'top'?
                        padding: [-60, 0, 0, 0],
                    },
                    type: 'category',
                    data: hours,
                    name: 'hours',
                    splitArea: {
                        show: true
                    }
                },
                visualMap: [{
                    min: this.getMinSD(remDataJson, "SD"),
                    max: this.getMaxSD(remDataJson, "SD"),
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
                    min: this.getMinSD(nremDataJson, "SD"),
                    max: this.getMaxSD(nremDataJson, "SD"),
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

                  this.toUpdate.push({
                    "x": removedData[0],
                    "y": removedData[1],
                    "stage": removedData[3]
                  })

                  // Modify the stage value
                  removedData[3] = 'nrem';

                  // Add to 'nrem' dataset
                  option.series[1].data.push(removedData);

                } else if (params.seriesIndex === 1) { // If the clicked series is 'nrem'
                  // Remove from 'nrem' dataset
                  let removedData = option.series[1].data.splice(params.dataIndex, 1)[0];

                  this.toUpdate.push({
                    "x": removedData[0],
                    "y": removedData[1],
                    "stage": removedData[3]
                  })

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
                let seriesIndex = params.seriesIndex;

                // Get the total number of data points in the selected series
                let seriesData = option.series[seriesIndex].data;
                let numDataPoints = seriesData.length;

                // Emphasize all data points in the selected series
                for (let i = 0; i < numDataPoints; i++) {
                  let dataIndex = `${seriesIndex}-${i}`;
                  this.selectedIndices.push(dataIndex);

                  // Emphasize each data point
                  myChart.dispatchAction({
                    type: 'highlight',
                    seriesIndex: seriesIndex,
                    dataIndex: i
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
            this.error = true;
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
