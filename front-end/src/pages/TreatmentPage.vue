<template>
    <el-row style="margin-bottom: 3%;">
        <el-col>
            <h1 style="text-align: center;">This is the Treatment Analysis page!</h1>
        </el-col>
    </el-row>
    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=4 />
        </el-col>
    </el-row>
    <el-row style="margin-top: 3%;">
        <el-col :span="18" :offset="6">
            <router-link :to="'/events-classification/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Events Classification</el-button>
            </router-link>
        </el-col>
    </el-row>

    <el-row style="margin-top: 3%;">
        <el-col :span="7" :offset="4">
            <div id="currentPatientHeatMap" style="position: relative; height: 70vh; width: 55vh"></div>
        </el-col>
        <el-col :span="2">
            Metrics with legend
        </el-col>
        <el-col :span="5">
            <el-row>
                <el-col :offset="4" style="margin-bottom:5%">
                    <p><b>Select the desired weeks</b></p>
                    <!--
                    <el-select
                    v-model="selectedWeeks"
                    multiple
                    placeholder="Select"
                    style="width: 240px"
                    >
                    <el-option
                        v-for="week in weeks"
                        :key="week.value"
                        :label="week.label"
                        :value="week.value"
                    />
                    </el-select>
                -->
                <el-slider v-model="week" :min="0" :max="Object.keys(weeks).length" range show-stops :marks="weeks" :show-tooltip="false" @change="changeWeekFilter" />
                </el-col>
            </el-row>
            <el-row>
                <el-col>
                    <div id="patientsLinePlot" style="position: relative; height: 68vh; width: 88vh"></div>
                </el-col>
            </el-row>
        </el-col>
        <el-col :span="4" :offset="2">
            Metrics
        </el-col>
    </el-row>
    <el-row style="margin-top: 3%;">
        <el-checkbox v-model="showCohort" label="Compare to cohort" size="large" border @change="showCohortHeatMap"/>
    </el-row>

    <el-row v-if="showCohort" style="margin-top: 3%;">
        <el-col :span="6" :offset="4">
            <el-card>
                <h3>Select desired patients</h3>
                <el-checkbox v-model="patientsCheckBox['1']" label="Patient 1" size="large" />
                <el-checkbox v-model="patientsCheckBox['2']" label="Patient 2" size="large" />
            </el-card>
        </el-col>
        <el-col :span="8" :offset="4">
            <div id="cohortHeatMap" style="position: relative; height: 80vh; width: 65vh"></div>
        </el-col>
        <el-col :span="2">
            Metrics
        </el-col>
    </el-row>
    <el-row style="margin-top: 2em;">
        <el-col :offset="4" :span="8">
            <el-row>
                <el-progress style="display:block;margin: 0 auto" type="dashboard" :percentage="studyAccuracy" width="80" stroke-width="4" :color="colors" >
                    <template #default="{ percentage }">
                        <h3 class="percentage-value">{{ percentage }}%</h3>
                        <h5 class="percentage-label">Accuracy</h5>
                    </template>
                </el-progress>
            </el-row>
            <el-row style="text-align:center">
                <h5 style="display:block; margin: 5px auto">Model Performance for whole Study</h5>
            </el-row>
        </el-col>

        <el-col :span="8">
            <el-row>
                <el-progress style="display:block; margin: 0 auto" type="dashboard" :percentage="patientAccuracy" width="80" stroke-width="4" :color="colors" >
                    <template #default="{ percentage }">
                        <h3 class="percentage-value">{{ percentage }}%</h3>
                        <h5 class="percentage-label">Accuracy</h5>
                    </template>
                </el-progress>
            </el-row>

            <el-row style="text-align:center">
                <h5 style="display:block; margin: 5px auto">Model Performance for Patient {{ this.$store.state.patientId }}</h5>
            </el-row>
        </el-col>
    </el-row>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
import * as echarts from 'echarts';
import { ref, reactive } from 'vue';
import axios from 'axios';

export default {
    name: 'TreatmentPage',
    components: {
        Stepper,

    },
    data(){
        return{
            showCohort: ref(false),
            eventTrendData: [],
            week: ref([0, 0]),
            startWeek: ref(''),
            endWeek: ref(''),
            noPatients: 0,
            nightsNo: 0,
            selectedWeeks: ref([]),
            weeks: ref({}),
            patientsCheckBox: {
                '1' : ref(false),
                '2': ref(false)

            },
            studyAccuracy: this.$store.state.studyAccuracy,
            patientAccuracy: this.$store.state.patientAccuracy,
        }
    },
    async mounted() {
        await this.getEventTrendData();
        this.getWeeks();
        this.drawCurrentPatientHeatMap();
        this.drawPatientsLinePlot(this.startWeek, this.endWeek);    
    },
    methods: {
        removeDuplicates(arr) { 
            return arr.filter((item, 
                index) => arr.indexOf(item) === index); 
        },
        getWeeks(){
            console.log("Getting the weeks")

            let weekData = [];

            for (let i = 0; i < this.eventTrendData.length; i++) {
                for(const key in this.eventTrendData[i]) {
                    let week = this.eventTrendData[i][key]['week'];
                    if(week !== null){
                        weekData.push(week)
                    }
                } 
            }


            weekData = weekData.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));  
            weekData = this.removeDuplicates(weekData);
            //this.startWeek = weekData[0];
            //this.endWeek = weekData[weekData.length - 1]

            console.log("weekdata without duplicates")
            console.log(weekData)

            for (let i=weekData.length-1; i >= 0; i--){
                if(weekData[i].toLowerCase().indexOf("-") === -1){
                    console.log("week without -")
                    console.log(weekData[i])
                    if(weekData.includes(weekData[i]+"-"+String((parseInt(weekData[i])+1)))){
                        console.log(String((parseInt(weekData[i])+1)))
                        weekData.splice(weekData.indexOf(weekData[i]), 1);
                    }
                    if(weekData.includes(String((parseInt(weekData[i])-1))+"-"+weekData[i])){
                        weekData.splice(weekData.indexOf(weekData[i]), 1);
                    }      
                }
            }

            let minWeek = 0;
            let maxWeek = weekData.length-1;
            console.log(minWeek)
            console.log(maxWeek)
            this.week = ref([minWeek, maxWeek])

            
            let weekOptions = {};
    
            for(let i=0; i<weekData.length; i++){
                weekOptions[i] = weekData[i];
            }

            console.log(weekOptions);
            this.weeks = reactive(weekOptions);
            console.log("weeks length")
            console.log(Object.keys(this.weeks).length)
        },
        changeWeekFilter(){
            console.log("changing the line chart according to the weeks")
            console.log(this.week)
            this.startWeek = this.weeks[this.week[0]]
            this.endWeek = this.weeks[this.week[1]]

            this.drawPatientsLinePlot(this.startWeek, this.endWeek);



            
            
        },
        updateHeatMaps(){
            console.log("Updating the heatmaps.")
        },
        showCohortHeatMap(){
            console.log(this.showCohort.valueOf());
            if(this.showCohort.valueOf() === true){
                console.log("ciao")
                this.drawCohortHeatMap();
            }
        },
        async getEventTrendData(){
            const path = `http://127.0.0.1:5000/event-trend`
            const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            let payload = {
                            params: {
                                //patient_id: JSON.stringify([parseInt(this.$store.state.patientId)]),
                                patient_id: JSON.stringify([1, 2, 3]),
                            }
                        };

            console.log(payload);

            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log(res.data)
                    this.eventTrendData = res.data;
                    this.nightsNo = this.eventTrendData.length; 
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        getTypeText(type){
            let text = "";
            if(type === -1){
                text = ""
            }
            if (type === 0) {
                text = "Night owl"
            }
            if (type === 1) {
                text = "Early Bird"
            }
            return text;

        },
        drawPatientsLinePlot(startWeek, endWeek){
            var dom = document.getElementById("patientsLinePlot");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            var option;


            let series = [];
            let exist = false;
            for (let i = 0; i < this.eventTrendData.length; i++) {
                for (const key in this.eventTrendData[i]) {
                    let type = this.eventTrendData[i][key]['type'];
                    let text = this.getTypeText(type);
                    let week = this.eventTrendData[i][key]['week']
                    let night = this.eventTrendData[i][key]['night']
                    for (let j = 0; j < series.length; j++) {
                        if(night != null){
                            if(series[j].name === "Patient " + key){
                                series[j].data.push(this.eventTrendData[i][key]['count'])
                                series[j].texts.push(text);
                                series[j].weeks.push(week);
                                series[j].nights.push(night);

                                series[j+1].data.push(null)
                                series[j+1].texts.push(null)
                                series[j+1].weeks.push(null)
                                series[j+1].nights.push(null)
                                exist = true;
                            }
                        } else {
                            if(series[j].name === "Patient " + key + " interpolated"){
                                series[j].data.push(this.eventTrendData[i][key]['count'])
                                series[j].texts.push(text);
                                series[j].weeks.push(week);
                                series[j].nights.push(night);

                                series[j-1].data.push(null)
                                series[j-1].texts.push(null)
                                series[j-1].weeks.push(null)
                                series[j-1].nights.push(null)
                                exist = true;
                            }
                        }
                    }
                    
                    if (exist === false){
                        series.push({name: "Patient " + key, 
                                type: 'line',
                                showAllSymbol: true,
                                data: [],
                                texts: [],
                                weeks: [],
                                nights: [],
                                lineStyle: {
                                    normal: {
                                        color: ''
                                    }
                                },
                                itemStyle: {
                                    color: ''
                                }
                            })
                            
                        series.push({name: "Patient " + key + " interpolated", 
                                type: 'line',
                                showSymbol: false,
                                data: [],
                                texts: [],
                                weeks: [],
                                nights: [],
                                lineStyle: {
                                    normal: {
                                        type: 'dashed',
                                        opacity: 50,
                                        color: ''
                                    }
                                },
                                itemStyle: {
                                    color: ''
                                }
                                })
                                
                        if(night !== null){
                            series[series.length-2].data.push(this.eventTrendData[i][key]['count'])
                            series[series.length-2].texts.push(text)
                            series[series.length-2].weeks.push(week)
                            series[series.length-2].nights.push(night)
                        } else {
                            series[series.length-1].data.push(this.eventTrendData[i][key]['count'])
                            series[series.length-1].texts.push(text)
                            series[series.length-1].weeks.push(week)
                            series[series.length-1].nights.push(night)
                        }
                        exist = false;
                    }
                }
            }

            let colors = [
            "#5470c6",
            "#91cc75",
            "#fac858",
            "#ee6666",
            "#73c0de",
            "#3ba272",
            "#fc8452",
            "#9a60b4",
            "#ea7ccc"
        ];

            for(let i=0; i<series.length; i++){
                if(colors.length > series.length/2){
                    if((series[i].name.toLowerCase().indexOf("interpolated") === -1)){
                        series[i].lineStyle.normal.color = colors[i]
                        series[i].itemStyle.color = colors[i]
                    } else {
                        series[i].lineStyle.normal.color = colors[i-1]
                        series[i].itemStyle.color = 'transparent'
                    }
                }
            }

            this.noPatients = series.length;

            /* WEEK FILTER LOGIC: not working yet
            if(startWeek !== '' && endWeek !== ''){
                let weeksList = Object.values(this.weeks);
                console.log("GUARDA QUI")
                console.log(weeksList.indexOf(startWeek))
                console.log(weeksList.indexOf(endWeek)+1)
                let subWeeksList = weeksList.slice(weeksList.indexOf(startWeek), weeksList.indexOf(endWeek)+1)

                console.log(subWeeksList)
                console.log("UPDATE PARAMETERS")
                for(let i=0; i<series.length; i++){
                    let startWeekNr = 0;
                    let endWeekNr = subWeeksList.length-1;
                    let weeks = series[i].weeks;
                    let startIdFound = false;
                    let endIdFound = false;
                    let startWeekId;
                    let endWeekId;
                    console.log(startWeek);
                    console.log(endWeek);
                    
                    while(startIdFound === false && endIdFound === false){
                        try{
                            if(startWeekNr >= subWeeksList.length-1){
                                break;
                            }
                            startWeekId = weeks.indexOf(startWeek)
                    
                            if(startWeekId === -1){
                                startWeekNr ++;
                                startWeek = subWeeksList[startWeekNr]  
                            } else {
                                startIdFound = true;
                            }
                            
                        }
                        catch(err){
                            console.log(err)
                        }
                        try{
                            if(endWeekNr <= 0){
                                break;
                            }
                            endWeekId = weeks.lastIndexOf(endWeek);

                            if(endWeekId === -1){
                                endWeekNr --;
                                endWeek = subWeeksList[endWeekNr]
                            } else {
                                endIdFound = true;
                            }
                        }
                        catch(err) {
                            console.log(err)
                        }
                    }

                    console.log(startIdFound)
                    console.log(endIdFound)
                    console.log(startWeekId)
                    console.log(endWeekId)

                    if(startIdFound === true && endIdFound === true){
                        console.log("StartId TRUE endId TRUE")
                        series[i].data = series[i].data.slice(startWeekId, endWeekId+1)
                        series[i].texts = series[i].texts.slice(startWeekId, endWeekId+1)
                        series[i].weeks = series[i].weeks.slice(startWeekId, endWeekId+1)
                        series[i].nights = series[i].nights.slice(startWeekId, endWeekId+1)
                        
                        console.log(series[i].data)
                        console.log(startWeekId)
                        console.log(endWeekId)
            
                    }
                    if(startIdFound === true && endIdFound === false){
                        console.log("StartId TRUE endId FALSE")
                        series[i].data = series[i].data.slice(startWeekId)
                        series[i].texts = series[i].texts.slice(startWeekId)
                        series[i].weeks = series[i].weeks.slice(startWeekId)
                        series[i].nights = series[i].nights.slice(startWeekId)
                    }
                    else{
                        console.log("startId FALSE endId ?")
                        series[i].data = []
                        series[i].texts = []
                        series[i].weeks = []
                        series[i].nights = []
                    }           
                }
                console.log(series)
            }

            */

            let legend = [];

            for (let i=0; i<series.length; i++){
                legend.push(series[i].name)

                //if(series[i].name.toLowerCase().indexOf("interpolated") === -1) {
                //    legend.push(series[i].name)
                //}
            }

            var callback = (args) => {
                let nightId = series[args.seriesIndex].nights[args.dataIndex]
                let week = series[args.seriesIndex].weeks[args.dataIndex]
                
                if(nightId !== null && week !== null){
                    return args.marker + " <b>" + args.seriesName + "</b>: " + args.value + " events <br />" + series[args.seriesIndex].texts[args.dataIndex] + "<br /> Night id: " + nightId + "- Week: " + week
                }
                else {
                    return args.marker + " <b>" + args.seriesName + "</b>: " + args.value + " events <br />" + series[args.seriesIndex].texts[args.dataIndex]
                }
            }
        


            option = {
                title: {
                    text: 'Interpolated events trend over days',
                    textAlign: 'left'
                },
                tooltip: {
                    trigger: 'item',
                    formatter: callback,
                    axisPointer: 'link'
                },
                legend: {
                    data: legend,
                    orient: 'horizontal',
                    right: 'right'
                },
                grid: {
                    left: '3%',
                    right: '4%',
                    bottom: '3%',
                    containLabel: true
                },
                toolbox: {
                    feature: {
                    saveAsImage: {}
                    }
                },
                dataZoom : {
                    show : true,
                    realtime: true,
                    start : 0,
                    end : this.nightsNo
                },
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    name: "Day",
                    data: [...Array(this.nightsNo).keys()],
                },
                yAxis: {
                    type: 'value',
                    name: 'Events'
        
                },
                series: series
            };

            if (option && typeof option === "object") {
                myChart.setOption(option);
            }
            window.addEventListener("resize", myChart.resize);
        },
        drawCurrentPatientHeatMap(){
            var dom = document.getElementById("currentPatientHeatMap");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            // var app = {};

            var option;

            // prettier-ignore
            const stages = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const days = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const data = [[0, 0, 5], [0, 1, 1], [0, 2, 0],  [2, 4, 4], [2, 5, 2], [2, 7, 3], [5, 6, 2], [5, 4, 3], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [7, 1, 0], [7, 2, 2], [7, 3, 4], [7, 4, 1], [7, 5, 1], [7, 6, 3], [8, 6, 4], [8, 7, 6], [9, 8, 4], [10, 9, 4], [14, 2, 3], [16, 1, 3], [18, 8, 2], [19, 6, 5], [1, 0, 7], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 6, 0], [1, 7, 0], [1, 8, 0], [1, 9, 0], [1, 10, 5], [1, 11, 2], [1, 12, 2], [1, 13, 6], [1, 14, 9], [1, 15, 11], [1, 16, 6], [1, 17, 7], [1, 18, 8], [1, 19, 12], [1, 20, 5], [1, 21, 5], [1, 22, 7], [1, 23, 2], [2, 0, 1], [2, 1, 1], [2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 5, 0], [2, 6, 0], [2, 7, 0], [2, 8, 0], [2, 9, 0], [2, 10, 3], [2, 11, 2], [2, 12, 1], [2, 13, 9], [2, 14, 8], [2, 15, 10], [2, 16, 6], [2, 17, 5], [2, 18, 5], [2, 19, 5], [2, 20, 7], [2, 21, 4], [2, 22, 2], [2, 23, 4], [3, 2, 0], [3, 3, 0], [3, 4, 0], [3, 5, 0], [3, 6, 0], [3, 7, 0], [3, 8, 1], [3, 9, 0], [3, 10, 5], [3, 11, 4], [3, 12, 7], [3, 13, 14], [3, 14, 13], [3, 15, 12], [3, 16, 9], [3, 17, 5], [3, 18, 5], [3, 19, 10], [3, 20, 6], [3, 21, 4], [3, 22, 4], [3, 23, 1], [4, 0, 1], [4, 1, 3], [4, 2, 0], [4, 3, 0], [4, 4, 0], [4, 5, 1], [4, 6, 0], [4, 7, 0], [4, 8, 0], [4, 9, 2], [4, 10, 4], [4, 11, 4], [4, 12, 2], [4, 13, 4], [4, 14, 4], [4, 15, 14], [4, 16, 12], [4, 17, 1], [4, 18, 8], [4, 19, 5], [4, 20, 3], [4, 21, 7], [4, 22, 3], [4, 23, 0], [5, 0, 2], [5, 1, 1], [5, 2, 0], [5, 3, 3], [5, 4, 0], [5, 5, 0], [5, 6, 0], [5, 7, 0], [5, 8, 2], [5, 9, 0], [5, 10, 4], [5, 11, 1], [5, 12, 5], [5, 13, 10], [5, 14, 5], [5, 15, 7], [5, 16, 11], [5, 17, 6], [5, 18, 0], [5, 19, 5], [5, 20, 3], [5, 21, 4], [5, 22, 2], [5, 23, 0], [6, 0, 1], [6, 1, 0], [6, 2, 0], [6, 3, 0], [6, 4, 0], [6, 5, 0], [6, 6, 0], [6, 7, 0], [6, 8, 0], [6, 9, 0], [6, 10, 1], [6, 11, 0], [6, 12, 2], [6, 13, 1], [6, 14, 3], [6, 15, 4], [6, 16, 0], [6, 17, 0], [6, 18, 0], [6, 19, 0], [6, 20, 1], [6, 21, 2], [6, 22, 2], [6, 23, 6]]
                .map(function (item) {
                return [item[1], item[0], item[2] || '-'];
            });

            var callback = (args) => {
                if (args.value[2] === 1){
                    return args.seriesName + "<br />" +args.marker + 'day '+parseInt(parseInt(args.value[0])+1) + ": " + args.value[2] + ' event(s)'

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
                    rotate: 30,
                    data: stages,
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
                    bottom: '30%'
                },
                series: [
                {
                    name: '<b>Details</b>',
                    type: 'heatmap',
                    data: data,
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

        },
        drawGlobalCurrentPatientHeatMap(){
            var dom = document.getElementById("currentPatientGlobalHeatMap");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            // var app = {};

            var option;

            // prettier-ignore
            const stages = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const days = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const data = [[0, 0, 5], [0, 1, 1], [0, 2, 0],  [2, 4, 4], [2, 5, 2], [2, 7, 3], [5, 6, 2], [5, 4, 3], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [7, 1, 0], [7, 2, 2], [7, 3, 4], [7, 4, 1], [7, 5, 1], [7, 6, 3], [8, 6, 4], [8, 7, 6], [9, 8, 4], [10, 9, 4], [14, 2, 3], [16, 1, 3], [18, 8, 2], [19, 6, 5], [1, 0, 7], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 6, 0], [1, 7, 0], [1, 8, 0], [1, 9, 0], [1, 10, 5], [1, 11, 2], [1, 12, 2], [1, 13, 6], [1, 14, 9], [1, 15, 11], [1, 16, 6], [1, 17, 7], [1, 18, 8], [1, 19, 12], [1, 20, 5], [1, 21, 5], [1, 22, 7], [1, 23, 2], [2, 0, 1], [2, 1, 1], [2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 5, 0], [2, 6, 0], [2, 7, 0], [2, 8, 0], [2, 9, 0], [2, 10, 3], [2, 11, 2], [2, 12, 1], [2, 13, 9], [2, 14, 8], [2, 15, 10], [2, 16, 6], [2, 17, 5], [2, 18, 5], [2, 19, 5], [2, 20, 7], [2, 21, 4], [2, 22, 2], [2, 23, 4], [3, 2, 0], [3, 3, 0], [3, 4, 0], [3, 5, 0], [3, 6, 0], [3, 7, 0], [3, 8, 1], [3, 9, 0], [3, 10, 5], [3, 11, 4], [3, 12, 7], [3, 13, 14], [3, 14, 13], [3, 15, 12], [3, 16, 9], [3, 17, 5], [3, 18, 5], [3, 19, 10], [3, 20, 6], [3, 21, 4], [3, 22, 4], [3, 23, 1], [4, 0, 1], [4, 1, 3], [4, 2, 0], [4, 3, 0], [4, 4, 0], [4, 5, 1], [4, 6, 0], [4, 7, 0], [4, 8, 0], [4, 9, 2], [4, 10, 4], [4, 11, 4], [4, 12, 2], [4, 13, 4], [4, 14, 4], [4, 15, 14], [4, 16, 12], [4, 17, 1], [4, 18, 8], [4, 19, 5], [4, 20, 3], [4, 21, 7], [4, 22, 3], [4, 23, 0], [5, 0, 2], [5, 1, 1], [5, 2, 0], [5, 3, 3], [5, 4, 0], [5, 5, 0], [5, 6, 0], [5, 7, 0], [5, 8, 2], [5, 9, 0], [5, 10, 4], [5, 11, 1], [5, 12, 5], [5, 13, 10], [5, 14, 5], [5, 15, 7], [5, 16, 11], [5, 17, 6], [5, 18, 0], [5, 19, 5], [5, 20, 3], [5, 21, 4], [5, 22, 2], [5, 23, 0], [6, 0, 1], [6, 1, 0], [6, 2, 0], [6, 3, 0], [6, 4, 0], [6, 5, 0], [6, 6, 0], [6, 7, 0], [6, 8, 0], [6, 9, 0], [6, 10, 1], [6, 11, 0], [6, 12, 2], [6, 13, 1], [6, 14, 3], [6, 15, 4], [6, 16, 0], [6, 17, 0], [6, 18, 0], [6, 19, 0], [6, 20, 1], [6, 21, 2], [6, 22, 2], [6, 23, 6]]
                .map(function (item) {
                return [item[1], item[0], item[2] || '-'];
            });

            var callback = (args) => {
                if (args.value[2] === 1){
                    return args.seriesName + "<br />" +args.marker + 'day '+parseInt(parseInt(args.value[0])+1) + ": " + args.value[2] + ' event(s)'

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
                    rotate: 30,
                    data: stages,
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
                    bottom: '30%'
                },
                series: [
                {
                    name: '<b>Details</b>',
                    type: 'heatmap',
                    data: data,
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

        },
        drawCohortHeatMap(){
            var dom = document.getElementById("cohortHeatMap");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            // var app = {};

            var option;

            // prettier-ignore
            const stages = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const days = Array.from({length: 7}, (_, i) => i + 1);
            // prettier-ignore
            const data = [[0, 0, 5], [0, 1, 1], [0, 2, 0],  [2, 4, 4], [2, 5, 2], [2, 7, 3], [5, 6, 2], [5, 4, 3], [0, 3, 0], [0, 4, 0], [0, 5, 0], [0, 6, 0], [0, 7, 0], [0, 8, 0], [0, 9, 0], [7, 1, 0], [7, 2, 2], [7, 3, 4], [7, 4, 1], [7, 5, 1], [7, 6, 3], [8, 6, 4], [8, 7, 6], [9, 8, 4], [10, 9, 4], [14, 2, 3], [16, 1, 3], [18, 8, 2], [19, 6, 5], [1, 0, 7], [1, 1, 0], [1, 2, 0], [1, 3, 0], [1, 4, 0], [1, 5, 0], [1, 6, 0], [1, 7, 0], [1, 8, 0], [1, 9, 0], [1, 10, 5], [1, 11, 2], [1, 12, 2], [1, 13, 6], [1, 14, 9], [1, 15, 11], [1, 16, 6], [1, 17, 7], [1, 18, 8], [1, 19, 12], [1, 20, 5], [1, 21, 5], [1, 22, 7], [1, 23, 2], [2, 0, 1], [2, 1, 1], [2, 2, 0], [2, 3, 0], [2, 4, 0], [2, 5, 0], [2, 6, 0], [2, 7, 0], [2, 8, 0], [2, 9, 0], [2, 10, 3], [2, 11, 2], [2, 12, 1], [2, 13, 9], [2, 14, 8], [2, 15, 10], [2, 16, 6], [2, 17, 5], [2, 18, 5], [2, 19, 5], [2, 20, 7], [2, 21, 4], [2, 22, 2], [2, 23, 4], [3, 2, 0], [3, 3, 0], [3, 4, 0], [3, 5, 0], [3, 6, 0], [3, 7, 0], [3, 8, 1], [3, 9, 0], [3, 10, 5], [3, 11, 4], [3, 12, 7], [3, 13, 14], [3, 14, 13], [3, 15, 12], [3, 16, 9], [3, 17, 5], [3, 18, 5], [3, 19, 10], [3, 20, 6], [3, 21, 4], [3, 22, 4], [3, 23, 1], [4, 0, 1], [4, 1, 3], [4, 2, 0], [4, 3, 0], [4, 4, 0], [4, 5, 1], [4, 6, 0], [4, 7, 0], [4, 8, 0], [4, 9, 2], [4, 10, 4], [4, 11, 4], [4, 12, 2], [4, 13, 4], [4, 14, 4], [4, 15, 14], [4, 16, 12], [4, 17, 1], [4, 18, 8], [4, 19, 5], [4, 20, 3], [4, 21, 7], [4, 22, 3], [4, 23, 0], [5, 0, 2], [5, 1, 1], [5, 2, 0], [5, 3, 3], [5, 4, 0], [5, 5, 0], [5, 6, 0], [5, 7, 0], [5, 8, 2], [5, 9, 0], [5, 10, 4], [5, 11, 1], [5, 12, 5], [5, 13, 10], [5, 14, 5], [5, 15, 7], [5, 16, 11], [5, 17, 6], [5, 18, 0], [5, 19, 5], [5, 20, 3], [5, 21, 4], [5, 22, 2], [5, 23, 0], [6, 0, 1], [6, 1, 0], [6, 2, 0], [6, 3, 0], [6, 4, 0], [6, 5, 0], [6, 6, 0], [6, 7, 0], [6, 8, 0], [6, 9, 0], [6, 10, 1], [6, 11, 0], [6, 12, 2], [6, 13, 1], [6, 14, 3], [6, 15, 4], [6, 16, 0], [6, 17, 0], [6, 18, 0], [6, 19, 0], [6, 20, 1], [6, 21, 2], [6, 22, 2], [6, 23, 6]]
                .map(function (item) {
                return [item[1], item[0], item[2] || '-'];
            });

            var callback = (args) => {
                if (args.value[2] === 1){
                    return args.seriesName + "<br />" +args.marker + 'day '+parseInt(parseInt(args.value[0])+1) + ": " + args.value[2] + ' event(s)'

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
                    rotate: 30,
                    data: stages,
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
                    bottom: '30%'
                },
                series: [
                {
                    name: '<b>Details</b>',
                    type: 'heatmap',
                    data: data,
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