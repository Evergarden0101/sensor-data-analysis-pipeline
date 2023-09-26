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
    title="Do you want to the events detection phase with the currently selected values?"
    confirm-button-text="Yes"
    cancel-button-text="Select again"
    @confirm="toggleEditMode"
    @cancel="exitEditMode"
    width="350">
        <template #reference>
            <el-button v-if="isEditMode">Exit Edit Mode</el-button>
        </template>
    </el-popconfirm>
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
      selectedOnDb: [],
      loading: ref(true),
      isEditMode: false,
      error: false,
      clicked: [],
      firstEnteredEditMode: false,
    }
  },
  async mounted() {
    this.drawTreatHeatMap(this.$store.state.patientId, this.$store.state.week, this.$store.state.nightId);

    await this.getCurrentlySelected()
  },
  methods: {
    open() {
        ElMessage('Please choose the cell for which you want to modify the label.')
    },
    getSubtitle(){
        return "No dataset found for user " + this.$store.state.patientId + " on night " + this.$store.state.nightId + " of week " + this.$store.state.week + "."
    },
    arrayEquals(a, b){
        return a.length === b.length && a.every((item,idx) => item === b[idx])
    },
    getMaxSD(arr1, arr2, prop) {
        var max1;
        var max2;
        if(arr1.length === 0){
            max1 = 0;
        }
        if(arr2.length === 0){
            max2 = 0;
        }
        if(arr1.length > 0 || arr2.length >0){
            for (var i=0 ; i<arr1.length ; i++) {
                if (max1 == null || parseInt(arr1[i][prop]) > parseInt(max1[prop]))
                    max1 = arr1[i];
            }

            for (var i=0 ; i<arr2.length ; i++) {
                if (max2 == null || parseInt(arr2[i][prop]) > parseInt(max2[prop]))
                    max2 = arr2[i];
            }


            return Math.max(max1.SD, max2.SD);
        }

        
    },
    getMinSD(arr1, arr2, prop) {
        var min1;
        var min2;
        if(arr1.length === 0 ){
            min1 = 0
        }
        if(arr2.length === 0){
            min2 = 0
        }
        if(arr1.length > 0 || arr2.length >0){
           for (var i=0 ; i<arr1.length ; i++) {
            if (min1 == null || parseInt(arr1[i][prop]) < parseInt(min1[prop]))
                min1 = arr1[i];
            }

            for (var i=0 ; i<arr2.length ; i++) {
            if (min2 == null || parseInt(arr2[i][prop]) < parseInt(min2[prop]))
                min2 = arr2[i];
            }

            return Math.min(min1.SD, min2.SD)
        }

        
    },

    toggleEditMode() {
      this.isEditMode = !this.isEditMode;
      this.firstEnteredEditMode = true;
      if(!this.isEditMode){
        const path = `http://localhost:5000/selected-sleep-phases/${this.$store.state.patientId}/${this.$store.state.week}/${this.$store.state.nightId}`
        const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
        };

        let payload = [];

        for(let i=0; i<this.clicked.length; i++){
            payload.push({
                "x": this.clicked[i][0],
                "y": this.clicked[i][1],
            })
        }
        
        axios.post(path, payload, {headers})
            .then((res) => {
                this.clicked = [];
                this.$router.push('/bruxism/');

            })
            .catch(err=>{
                console.log(err)
            })

      }

    },
    async getCurrentlySelected(){
        const path = `http://localhost:5000/selected-sleep-phases/${this.$store.state.patientId}/${this.$store.state.week}/${this.$store.state.nightId}`
        const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
        };

        await axios.get(path, {headers})
            .then((res) => {
                console.log("DATA RECEIVED!")
                console.log(res.data);
                this.clicked = res.data;
                this.dataReceived = true;
            })
            .catch(err=>{
                console.log(err)
            })
    },
    exitEditMode(){
        this.isEditMode = !this.isEditMode;
        this.clicked = [];
        this.$router.go();
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
                return [item['x'], item['y'], Math.round(item['SD']), item['stage'], item['LF_HF']];
            });

            var nremData = nremDataJson.map(function (item) {
                return [item['x'], item['y'], Math.round(item['SD']), item['stage'], item['LF_HF']];
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
                    min: this.getMinSD(remDataJson, nremDataJson, "SD"),
                    max: this.getMaxSD(remDataJson, nremDataJson, "SD"),
                    text: ["high", "low"],
                    dimension: 2,
                    inRange : {
                        color: ['#1919ff', '#CCCCFF'] //From bigger to smaller value ->
                    },
                    seriesIndex : 0,
                    calculable: false,
                    orient: 'horizontal',
                    left: 'center',
                    bottom: '30%',
                }, {
                    min: this.getMinSD(nremDataJson, remDataJson, "SD"),
                    max: this.getMaxSD(nremDataJson, remDataJson, "SD"),
                    text: ["high", "low"],
                    dimension: 2,
                    inRange : {
                        color: ['#999999', '#eeeeee'] //From bigger to smaller value ->
                    },
                    seriesIndex : 1,
                    calculable: false,
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
                            borderColor: 'black',
                            borderWidth: 3
                        }
                    }
                }, {
                    name: '<b>LF/HF ratio ± Standard Deviation (SD)</b>',
                    type: 'heatmap',
                    data: nremData,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)',
                            borderColor: 'black',
                            borderWidth: 3
                        }
                    }
                }]
            };


            myChart.on('click', (params) => {
              console.log('Tile clicked:', params);
            

              if(this.firstEnteredEditMode){
                console.log("FIRST")
                let remData = option.series[0].data
                if(!this.dataReceived || this.clicked.length === 0){
                    console.log("Data not received")
                    for(const key in remData){
                        this.clicked.push(remData[key])
                        myChart.dispatchAction({
                            type: 'highlight',
                            seriesIndex: 0,
                            dataIndex: key
                        })
                    }
                } else {
                    for(let i=0; i<this.clicked.length; i++){
                        if (this.clicked[i][3] === 'rem'){
                            let dataSeries = option.series[0].data;
                            for(const key in dataSeries){
                                if (JSON.stringify(dataSeries[key]) === JSON.stringify(this.clicked[i])){
                                    myChart.dispatchAction({
                                    type: 'highlight',
                                    seriesIndex: 0,
                                    dataIndex: key
                                })

                                } 
                            }
                        } else {
                            let dataSeries = option.series[1].data;
                            for(const key in dataSeries){
                                if (JSON.stringify(dataSeries[key]) === JSON.stringify(this.clicked[i])){
                                    myChart.dispatchAction({
                                    type: 'highlight',
                                    seriesIndex: 1,
                                    dataIndex: key
                                })

                                } 
                            }
                        }
                        
                    }

                }
                
                this.firstEnteredEditMode = !this.firstEnteredEditMode;
              } else {
                if(JSON.stringify(this.clicked).includes(JSON.stringify(params.data))){
                    console.log("includes")
                    this.clicked = this.clicked.filter(item => !this.arrayEquals(item, params.data))
                    myChart.dispatchAction({
                        type: 'downplay',
                        seriesIndex: params.seriesIndex,
                        dataIndex: params.dataIndex
                    })

                } else {
                    console.log("ELSE")
                    this.clicked.push(params.data)
                    myChart.dispatchAction({
                        type: 'highlight',
                        seriesIndex: params.seriesIndex,
                        dataIndex: params.dataIndex
                    })
                }

              }
            
              if (this.isEditMode) {
                if (params.seriesIndex === 0) { // If the clicked series is 'rem'

                    console.log("CLICKED REM")
                  // Remove from 'rem' dataset
                  let tileClicked = params.data;

                  console.log(params.data)

                } else if (params.seriesIndex === 1) { // If the clicked series is 'nrem'
                  // Remove from 'nrem' dataset
                  console.log("CLICKED NREM")
                  let tileClicked = params.data;
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
