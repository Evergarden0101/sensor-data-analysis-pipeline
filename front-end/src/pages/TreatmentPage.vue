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
        <el-col :span="4" :offset="2">
            <el-progress style="display:block;margin: 0 auto" type="dashboard" :percentage="studyPrecision" width="80" stroke-width="4" >
                <template #default="{ percentage }">
                    <h3 class="percentage-value">{{ percentage }}%</h3>
                    <h5 class="percentage-label">Precision</h5>
                </template>
            </el-progress>
        </el-col>
        <el-col :span="4" :offset="2">
            <el-row>
                <el-progress style="display:block; margin: 0 auto" type="dashboard" :percentage="patientPrecision" width="80" stroke-width="4" >
                    <template #default="{ percentage }">
                        <h3 class="percentage-value">{{ percentage }}%</h3>
                        <h5 class="percentage-label">Precision</h5>
                    </template>
                </el-progress>
            </el-row>
        </el-col>
        <el-col :span="10" :offset="2">
            Other metrics...
        </el-col>
    </el-row>


    <el-row style="border-bottom: solid grey; border-top:solid grey; margin-top: 2%;">
        <el-col :span="8" :offset="2" style="border-right:solid; border-color: grey">
            <h2>Patient {{ this.$store.state.patientId }} - Weekly summary for week {{ this.$store.state.week }}</h2>
            <div v-if="patientsExists" id="currentPatientHeatMap" style="position: relative; height: 70vh; width: 55vh; margin-top:10%"></div>
            <div v-else>
                <el-empty :image-size="70" description="Select at least a patient to see heatmap"/>
            </div>

          <el-col style="margin-top: -25%; margin-right: 40%">
            <div class="kpi-container">
              <div><strong>Average Events per Cycle:</strong> {{ averageEventsPerCycle.toFixed(2) }}</div>
              <div><strong>Total Events:</strong> {{ totalEvents }}</div>
            </div>
          </el-col>

        </el-col>

        <el-col :span="9" :offset="1" style="margin-bottom:5%">
            <h2>Comparison between patients</h2>
            <p><b>Select the desired weeks</b></p>
            <div style="display: flex;align-items: center;">
                <el-slider v-model="week" :min="minWeekId" :max="maxWeekId" range show-stops :marks="weekMarks" :format-tooltip="formatTooltip" @change="changeWeekFilter" />
            </div>        
            <div v-if="patientsExists" id="patientsLinePlot" style="position: relative; height: 50vh; width: 70vh; margin-top: 10%;"></div>
            <div v-else>
                <el-empty :image-size="200" description="Select at least a patient to see linechart"/>
            </div>
        </el-col>
        <el-col :span="2" :offset="1">
            <el-card>
                <h3>Select desired patients</h3>
                <el-checkbox v-for="patientId of patientsIds" v-model="patientsCheckBox[patientId]" :label="'Patient '+patientId" size="large" @change="handlePatientsSelection(patientId)"/>
            </el-card>
        </el-col>
    </el-row>
    <el-row v-if="selectedPatients.length >= 3">
        <h2>Comparison between patients - Single plots</h2>
        <el-col>
            <div style="display: flex; flex-wrap: wrap; padding:40px">
                <div v-for="patientId in selectedPatients" style="flex-grow: 1; width: 33%; height: 100px;">
                    <div v-if="patientsExists" :id="'patient'+patientId+'LineChart'" style="position: relative; height: 40vh; width: 60vh; margin-top: 3%;"></div>
                </div>
            </div>
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
            patientsExists: ref(false),
            eventTrendData: [],
            week: ref([0, 0]),
            startWeek: ref(-1),
            endWeek: ref(-1),
            minWeekId: ref(0),
            maxWeekId: ref(0),
            nightsNo: 0,
            patientsIds: ref([]),
            selectedPatients: [parseInt(this.$store.state.patientId)],
            selectedWeeks: ref([]),
            weeks: ref({}),
            completeWeekList: ref({}),
            weekMarks: ref({}),
            patientsCheckBox: {},
            studyPrecision: this.$store.state.studyPrecision,
            patientPrecision: this.$store.state.patientPrecision,
            patientsColorEncoding:{},
            colors: [
                "#5470c6",
                "#91cc75",
                "#fac858",
                "#ee6666",
                "#73c0de",
                "#3ba272",
                "#fc8452",
                "#9a60b4",
                "#ea7ccc"
            ],
            weeklySummaryData: [],
            averageEventsPerCycle: 0,
            totalEvents: 0,
        }
    },
    async mounted() {
        await this.getExistingEventTrendPatientIds();
        await this.getEventTrendData(this.selectedPatients);
        await this.getWeeklySummary();
        await this.getWeeks();
        await this.drawPatientsLinePlot(this.startWeek, this.endWeek);
    },
    methods: {
        findWeekIndex(weeks, value){
            var index=-1;
            for(const key in weeks){
                if(weeks[key].includes(value)){
                    index = key;
                }
            }
            return index;
        },
        formatTooltip(val){
            return this.weeks[val]
        },
        removeDuplicates(arr) {
            return arr.filter((item,
                index) => arr.indexOf(item) === index);
        },
        async getWeeks(){
            console.log("Getting the weeks")

            var weeks = [];

            for (let i = 0; i < this.eventTrendData.length; i++) {
                for(const key in this.eventTrendData[i]) {
                    if(this.eventTrendData[i][key] !== null){
                        let week = this.eventTrendData[i][key].week;
                        if(week !== null){
                            weeks.push(week)
                        }
                    }
                }
            }

            weeks = [...new Set(weeks)]
            var weeksOrdered = weeks.sort((a, b) => a.localeCompare(b, undefined, { numeric: true }))

            const swapElements = (array, index1, index2) => {
                let temp = array[index1];
                array[index1] = array[index2];
                array[index2] = temp;
            };

            for(const i in weeksOrdered){
                if(String(weeksOrdered[i]).indexOf("-") !== -1){
                    const beforeSymbol = weeksOrdered[i].substring(0, weeksOrdered[i].indexOf("-"));
                    if(beforeSymbol === weeksOrdered[i-1]){
                        swapElements(weeksOrdered, i, i-1)
                    }
                }
            }
            console.log(weeksOrdered)

            let weekListOrder = {}

            var id = 0;
            for(let i=0; i<weeksOrdered.length; i++){
                if(String(weeksOrdered[i]).indexOf("-") !== -1){
                    weekListOrder[id] = [];
                    weekListOrder[id].push(weeksOrdered[i]);
                    
                    const beforeSymbol = String(weeksOrdered[i].split('-')[0]);
                    const afterSymbol = String(weeksOrdered[i].split('-')[1]);
                    
                    if(weeksOrdered.includes(beforeSymbol)){
                        weekListOrder[id].push(beforeSymbol)
                    }
                    if(weeksOrdered.includes(afterSymbol)){
                        weekListOrder[id].push(afterSymbol)
                    }
                    id++;
                } else {
                    var inList = false;
                    for(const key in weekListOrder){
                        if(weekListOrder[key].includes(weeksOrdered[i]) === true){
                            inList = true;
                        }
                    }
                    if(inList===false){
                        weekListOrder[id] = [];
                        weekListOrder[id].push(weeksOrdered[i])
                        id++;
                    }      
                }
            }

            console.log(weekListOrder)

            this.completeWeekList = reactive(weekListOrder)

            var weekOptions = {};
            var weekMarks = {};

            for(const key in weekListOrder){
                weekOptions[key] = String(weekListOrder[key][0]);
            }
            
            for(const i in weekOptions){
                if(i % 2 === 0){
                    weekMarks[i] = weekOptions[i]
                }
            }

            this.weeks = reactive(weekOptions);
            this.weekMarks = reactive(weekMarks);
            this.minWeekId = parseInt(Object.keys(weekOptions)[0])
            this.maxWeekId = parseInt(Object.keys(weekOptions)[Object.keys(weekOptions).length-1])

            this.week = ref([parseInt(this.minWeekId), parseInt(this.maxWeekId)])
        },
        async handlePatientsSelection(patientId){
            if(this.patientsCheckBox[patientId] === true){
                this.selectedPatients.push(parseInt(patientId))
                this.selectedPatients = this.selectedPatients.sort(function(a,b){return a-b});
                this.patientsExists = ref(true);
                await this.getEventTrendData(this.selectedPatients);
                await this.getWeeks();
                await this.drawPatientsLinePlot(this.startWeek, this.endWeek);
            } else {
                console.log("REMOVE")
                let index = this.selectedPatients.indexOf(parseInt(patientId))
                this.selectedPatients.splice(index, 1);
                
                if(this.selectedPatients.length === 0){
                    this.patientsExists = ref(false);
                } else {
                    this.selectedPatients = this.selectedPatients.sort(function(a,b){return a-b});
                    await this.getEventTrendData(this.selectedPatients);
                    await this.getWeeks();
                    await this.drawPatientsLinePlot(this.startWeek, this.endWeek);
                }
            }

            if(this.selectedPatients.length >= 3){
                this.selectedPatients = this.selectedPatients.sort(function(a,b){return a-b});
                console.log("SORTED")
                console.log(this.selectedPatients)
                for(let i=0; i<this.selectedPatients.length; i++){
                    console.log(this.selectedPatients[i])
                   this.drawSinglePatientLineChart(this.selectedPatients[i])
                }
            }
        },
        async changeWeekFilter(){
            console.log("changing the line chart according to the weeks")
            this.startWeek = this.week[0]
            this.endWeek = this.week[1]

            await this.drawPatientsLinePlot(this.startWeek, this.endWeek);
        },
        async getExistingEventTrendPatientIds(){
            const path = `http://127.0.0.1:5000/event-trend-patients-ids`
            const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            await axios.get(path, {headers})
                .then((res) => {
                    console.log(res.data);
                    this.patientsIds = res.data;
                    if(this.patientsIds.length > 0){
                        for(let i=0; i<this.patientsIds.length; i++){
                            if(this.patientsIds[i] === this.$store.state.patientId){
                                this.patientsCheckBox[this.patientsIds[i]] = ref(true);
                            } else {
                                this.patientsCheckBox[this.patientsIds[i]] = ref(false);
                            }
                        }
                        console.log("patientscheckbox")
                        console.log(this.patientsCheckBox)
                        this.patientsExists = ref(true);
                    }
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        async getEventTrendData(patientIds){
            const path = `http://127.0.0.1:5000/event-trend`
            const headers = {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            let payload = {
                            params: {
                                //patient_id: JSON.stringify([parseInt(this.$store.state.patientId)]),
                                patient_id: JSON.stringify(patientIds),
                            }
                        };

            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log(res.data)
                    this.eventTrendData = res.data;
                    this.nightsNo = this.eventTrendData.length;
                    console.log("nightsNo")
                    console.log(this.nightsNo)
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
        getSeries(result){

            let series = [];

            for(let i=0; i<result.length; i++){
                for(const key in result[i]){
                    var exist = false;

                    // CHECK IF PATIENT EXIST
                    for(let j=0; j<series.length; j++){
                        if(key === series[j].patientId){
                            exist = true;
                            if(result[i][key] === null){
                                //console.log("The data is null", series[j].patientId)
                                //The data is null
                                series[j].data.push(null)
                                series[j].texts.push(null);
                                series[j].weeks.push(null);
                                series[j].nights.push(null);
                                series[j].days.push(null);
                            }
                            else{
                                if(result[i][key].night !== null){
                                    if(series[j].name === "Patient " + key){
                                        series[j].data.push(result[i][key].count)
                                        series[j].texts.push(this.getTypeText(result[i][key].type));
                                        series[j].weeks.push(result[i][key].week);
                                        series[j].nights.push(result[i][key].night);
                                        series[j].days.push(result[i][key].day);
                                        }
                                    if(series[j].name == "Patient " + key + " interpolated"){
                                        series[j].data.push(null)
                                        series[j].texts.push(null);
                                        series[j].weeks.push(result[i][key].week);
                                        series[j].nights.push(null);
                                        series[j].days.push(result[i][key].day);
                                    }

                                } else {
                                    if(series[j].name === "Patient " + key){
                                        series[j].data.push(null)
                                        series[j].texts.push(this.getTypeText(result[i][key].type));
                                        series[j].weeks.push(result[i][key].week);
                                        series[j].nights.push(result[i][key].night);
                                        series[j].days.push(result[i][key].day);
                                    }
                                    if(series[j].name == "Patient " + key + " interpolated"){
                                        series[j].data.push(result[i][key].count)
                                        series[j].texts.push(null);
                                        series[j].weeks.push(result[i][key].week);
                                        series[j].nights.push(null);
                                        series[j].days.push(result[i][key].day);
                                    }
                                }
                            }
                        }
                    }


                    // PATIENT STILL DOES NOT EXIST
                    if(exist === false){
                        var seriesIndex = series.length;
                        if(result[i][key] === null){
                            series.push({
                            name: "Patient " + key,
                            type: 'line',
                            seriesIndex: seriesIndex,
                            showAllSymbol: true,
                            patientId: key,
                            data: [null],
                            texts: [null],
                            weeks: [null],
                            nights: [null],
                            days: [null],
                            lineStyle: {
                                normal: {
                                    color: ''
                                }
                            },
                            itemStyle: {
                                color: ''
                            }
                            })
                            series.push({
                            name: "Patient " + key + " interpolated",
                            type: 'line',
                            seriesIndex: seriesIndex+1,
                            showSymbol: false,
                            patientId: key,
                            data: [null],
                            texts: [null],
                            weeks: [null],
                            nights: [null],
                            days: [null],
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

                        }
                        else if(result[i][key].night !== null){
                            series.push({
                            name: "Patient " + key,
                            type: 'line',
                            seriesIndex: seriesIndex,
                            showAllSymbol: true,
                            patientId: key,
                            data: [result[i][key].count],
                            texts: [this.getTypeText(result[i][key].type)],
                            weeks: [result[i][key].week],
                            nights: [result[i][key].night],
                            days: [result[i][key].day],
                            lineStyle: {
                                normal: {
                                    color: ''
                                }
                            },
                            itemStyle: {
                                color: ''
                            }
                            })
                            series.push({
                            name: "Patient " + key + " interpolated",
                            type: 'line',
                            seriesIndex: seriesIndex+1,
                            showSymbol: false,
                            patientId: key,
                            data: [null],
                            texts: [null],
                            weeks: [result[i][key].week],
                            nights: [null],
                            days: [result[i][key].day],
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
                        }
                        else if (result[i][key].night === null){
                            series.push({
                            name: "Patient " + key,
                            type: 'line',
                            seriesIndex: seriesIndex,
                            showAllSymbol: true,
                            patientId: key,
                            data: [null],
                            texts: [null],
                            weeks: [result[i][key].week],
                            nights: [null],
                            days: [result[i][key].day],
                            lineStyle: {
                                normal: {
                                    color: ''
                                }
                            },
                            itemStyle: {
                                color: ''
                            }
                            })
                            series.push({
                            name: "Patient " + key + " interpolated",
                            type: 'line',
                            seriesIndex: seriesIndex+1,
                            showSymbol: false,
                            patientId: key,
                            data: [result[i][key].count],
                            texts: [null],
                            weeks: [result[i][key].week],
                            nights: [null],
                            days: [result[i][key].day],
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
                        }
                    }
                }
            }
            return series;
        },
        getFilteredSeries(startWeek, endWeek, series){
            var startWeekIndex = -1;
            var endWeekIndex = -1;
            var seriesToRemove = [];

            for(let i=0; i<series.length; i=i+2){
                var toInclude = [];
                for(let j=0; j<series[i].weeks.length; j++){
                    var curWeekId = this.findWeekIndex(this.completeWeekList, series[i].weeks[j])
                    if(curWeekId !== -1){
                        if((startWeek <= curWeekId) && (endWeek >= curWeekId)){
                            toInclude.push(series[i].weeks[j])
                        }
                    }
                }
                if(toInclude.length === 0){
                    seriesToRemove.push(i)
                    seriesToRemove.push(i+1)
                } else {
                    startWeekIndex = series[i].weeks.indexOf(toInclude[0])
                    endWeekIndex = series[i].weeks.lastIndexOf(toInclude[toInclude.length-1])
                    
                    series[i].data = series[i].data.slice(startWeekIndex, endWeekIndex+1)
                    series[i].texts = series[i].texts.slice(startWeekIndex, endWeekIndex+1)
                    series[i].weeks = series[i].weeks.slice(startWeekIndex, endWeekIndex+1)
                    series[i].nights = series[i].nights.slice(startWeekIndex, endWeekIndex+1)
                    series[i].days = series[i].days.slice(startWeekIndex, endWeekIndex+1)
                    
                    series[i+1].data = series[i+1].data.slice(startWeekIndex, endWeekIndex+1)
                    series[i+1].texts = series[i+1].texts.slice(startWeekIndex, endWeekIndex+1)
                    series[i+1].weeks = series[i+1].weeks.slice(startWeekIndex, endWeekIndex+1)
                    series[i+1].nights = series[i+1].nights.slice(startWeekIndex, endWeekIndex+1)
                    series[i+1].days = series[i+1].days.slice(startWeekIndex, endWeekIndex+1)
                }
            }

            if(seriesToRemove.length > 0){
                for (const i of seriesToRemove.reverse()) {
                    series.splice(i, 1);
                }
            }
            console.log("NEW SERIES");
            console.log(series)
            return series;
        },
        getMinAndMaxDayNo(series){
            var minDay = parseInt(series[0].days[0]);
            var maxDay = parseInt(series[0].days[0]);

            for(let i=0; i<series.length; i++){
                for(let j=0; j<series[i].days.length; j++){
                    if(parseInt(series[i].days[j]) < minDay){
                        minDay = parseInt(series[i].days[j]);
                    }
                    if(parseInt(series[i].days[j]) > maxDay){
                        maxDay = parseInt(series[i].days[j]);
                    }
                }
            }
            return [minDay, maxDay];
        },
        async drawPatientsLinePlot(startWeek, endWeek){
            var dom = document.getElementById("patientsLinePlot");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            var option;

            var series = this.getSeries(this.eventTrendData);
            var xAxisData = [...Array(this.nightsNo).keys()]

            for(let i=0; i<series.length; i++){
                if(this.colors.length > series.length/2){
                    if((series[i].name.toLowerCase().indexOf("interpolated") === -1)){
                        series[i].lineStyle.normal.color = this.colors[i];
                        series[i].itemStyle.color = this.colors[i];
                        this.patientsColorEncoding[series[i].patientId] = this.colors[i];
                    } else {
                        series[i].lineStyle.normal.color = this.colors[i-1];
                        series[i].itemStyle.color = 'transparent';
                    }
                }
            }

            if(startWeek !== -1 || endWeek !== -1){
                console.log("Week filter logic")
                series = this.getFilteredSeries(startWeek, endWeek, series);
                var minAndMaxDay = this.getMinAndMaxDayNo(series);
                xAxisData = Array.from({length: minAndMaxDay[1] - minAndMaxDay[0] + 1}, (_, i) => i + minAndMaxDay[0])
            }

            let legend = [];

            for (let i=0; i<series.length; i++){
                legend.push(series[i].name)

                //if(series[i].name.toLowerCase().indexOf("interpolated") === -1) {
                //    legend.push(series[i].name)
                //}
            }

            var callback = (args) => {
                console.log(series[args.seriesIndex])
                console.log(series[args.seriesId])
                console.log(series)
                console.log(args)
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
                    orient: 'vertical',
                    right:'-1%',
                    textStyle: {
                        fontSize: '10',
                    }
                },
                grid: {
                    width: '90%',
                    height:'90%',
                    right: '10%',
                    bottom: '3%',
                    containLabel: true
                },
                toolbox: {
                    feature: {
                    saveAsImage: {}
                    }
                },
                /*
                dataZoom : {
                    show : true,
                    realtime: true
                },
                */
                xAxis: {
                    type: 'category',
                    boundaryGap: false,
                    name: "Day",
                    data: xAxisData,
                },
                yAxis: {
                    type: 'value',
                    name: 'Events'

                },
                series: series
            };

            if (option && typeof option === "object") {
                console.log("setting options")
                console.log(option)
                myChart.clear();
                myChart.setOption(option, true);
            }
            window.addEventListener("resize", myChart.resize);
        },

        async getWeeklySummary() {
          try {
            const path = `http://127.0.0.1:5000/weekly-summary/${this.$store.state.patientId}/${this.$store.state.week}/`;
            const response = await axios.get(path);
            this.weeklySummaryData = response.data;

            let totalEvents = 0;
            let cycleCounts = {};

            // Iterate over the fetched data to calculate total events and events per cycle
            this.weeklySummaryData.forEach(item => {
              totalEvents += item.count;
              cycleCounts[item.cycle] = (cycleCounts[item.cycle] || 0) + item.count;
            });

            // Calculate average events per cycle
            this.averageEventsPerCycle = Object.values(cycleCounts).reduce((a, b) => a + b, 0) / Object.keys(cycleCounts).length;
            this.totalEvents = totalEvents;

            this.drawCurrentPatientHeatMap();  // Call to draw the heatmap
          } catch (error) {
            console.error('Error fetching weekly summary data:', error);
          }
        },

      drawCurrentPatientHeatMap(){
            var dom = document.getElementById("currentPatientHeatMap");
            var myChart = echarts.init(dom, null, {
              renderer: "svg",
              useDirtyRect: false
            });

            // Determine the maximum cycle number from the data
            let maxCycle = this.weeklySummaryData.reduce((max, item) => Math.max(max, item.max_cycle), 0);

            // Prepare the data for the heatmap
            let heatmapData = this.weeklySummaryData.map(item => {
              return [item.day_no, item.cycle - 1, item.count];
            });

            var option;

            // prettier-ignore
            const days = Array.from({length: 7}, (_, i) => i + 1);

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
                    text: "Amount of events per sleep cycle"
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
                    data: Array.from({ length: maxCycle }, (_, i) => i + 1),
                    splitArea: {
                        show: true
                    },
                    inverse: true
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
                myChart.setOption(option, true);
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
                myChart.setOption(option, true);
            }

            window.addEventListener("resize", myChart.resize);

        },
        drawSinglePatientLineChart(patientId){
            var dom = document.getElementById("patient"+patientId+"LineChart");
            var myChart = echarts.init(dom, null, {
                renderer: "sgv",
                useDirtyRect: false
            });
            var option;

            let data = [];

            for(let i=0; i<this.eventTrendData.length; i++){
                for(const key in this.eventTrendData[i]){
                    let o = {};
                    if(parseInt(key) === patientId){
                        o[key] = this.eventTrendData[i][key]
                        data.push(o)
                    }
                }
            }

            console.log(data);

            let series = this.getSeries(data);

            if(series.length > 0){
                if(series.length ===2){
                    series[0].lineStyle.normal.color = this.patientsColorEncoding[patientId];
                    series[0].itemStyle.color = this.patientsColorEncoding[patientId];
                    series[1].lineStyle.normal.color = this.patientsColorEncoding[patientId];
                    series[1].itemStyle.color = 'transparent';
                }
                if(series.length===1){
                    series[0].lineStyle.normal.color = this.patientsColorEncoding[patientId];
                    series[0].itemStyle.color = this.patientsColorEncoding[patientId];
                }
            }


            let legend = [];

            for (let i=0; i<series.length; i++){
                legend.push(series[i].name)

                //if(series[i].name.toLowerCase().indexOf("interpolated") === -1) {
                //    legend.push(series[i].name)
                //}
            }

            var callback = (args) => {
                console.log(series[args.seriesIndex])
                console.log(series[args.seriesId])
                console.log(series)
                console.log(args)
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
                    text: 'Interpolated events trend over days of patient' + patientId ,
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
                    right: 'right',
                    top: 20
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
                console.log("setting options")
                console.log(option)
                myChart.setOption(option, true);
            }
            window.addEventListener("resize", myChart.resize);

        }
    }
}
</script>

<style scoped>
.kpi-container {
  text-align: center;
  padding: 20px;
  background-color: #f5f5f5;
  border-radius: 8px;
  margin: 20px 0;
}
.kpi-container > div {
  margin: 10px 0;
}
</style>

