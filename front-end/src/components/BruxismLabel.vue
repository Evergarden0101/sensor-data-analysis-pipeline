<template>
    <el-row>
        <el-card class="box-card" shadow="always" style="border: solid 2px;border-radius: 15px; width: 100%; margin-left: auto;margin-right: auto; padding:0;">
            <el-row>
                <el-col :span="12" :offset="6">
                    <h3 align="center" style="margin-top:-5px">Events Predictions</h3>
                </el-col>
                <el-col :span="6" style="margin-top:-9px">
                    <el-button type='primary' text='primary' @click="openDialog" style="">
                        Add Event
                    </el-button>
                    <el-dialog v-model="dialogFormVisible" title="Add Event" center width="30%" align-center draggable>
                        <el-form :model="form">
                            <el-form-item label="Start Time:" :label-width="formLabelWidth">
                                <el-input-number v-model="form.Start" style="width: 90px; margin-left: 20px;"  :controls="false" />
                                    <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                            </el-form-item>
                            <el-form-item label="End Time:" :label-width="formLabelWidth">
                                <el-input-number v-model="form.End" style="width: 90px;margin-left: 20px;"  :controls="false" />
                                    <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                            </el-form-item>
                        </el-form>
                        <template #footer>
                            <span class="dialog-footer">
                                <el-button @click="dialogFormVisible = false">Cancel</el-button>
                                <el-button type="primary" @click="submitNewLable">
                                Confirm
                                </el-button>
                            </span>
                        </template>
                    </el-dialog>
                </el-col>
            </el-row>

            <el-row style="margin-bottom:1em">
                <el-col :span="6">
                    <b style="display: block;margin: auto;">Comfirm events before rerun.</b>
                </el-col>
                <el-col :span="6">
                    <el-button @click="confirmLabel" type="primary" plain size="middle"
                        style="display: block;margin: 0 auto">Comfirm Events</el-button>
                </el-col>
                <el-col :span="6">
                    <LabelButton :labels="Labels" color="#626aef" plain size="middle"
                        style="display: block;margin: 0 auto"/>
                </el-col>
                <el-col :span="4" :offset="2">
                    <el-popover
                        :width="300"
                        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
                        >
                        <template #reference>
                            <!-- <el-avatar src="https://avatars.githubusercontent.com/u/72015883?v=4" /> -->
                            <el-icon size="25px"><Odometer /></el-icon>
                        </template>
                        <template #default>
                            <el-row style="">
                                <el-col :offset="1" :span="10">
                                    <el-row>
                                        <el-progress style="display:block;margin: 0 auto" type="dashboard" :percentage="studyPrecision" width="80" stroke-width="4" :color="colors" >
                                            <template #default="{ percentage }">
                                                <h3 class="percentage-value">{{ percentage }}%</h3>
                                                <h5 class="percentage-label">Precision</h5>
                                            </template>
                                        </el-progress>
                                    </el-row>
                                    <el-row style="text-align:center">
                                        <h5 style="display:block; margin: 5px auto">Model Performance for whole Study</h5>
                                    </el-row>
                                </el-col>

                                <el-col :span="10" :offset="2">
                                    <el-row>
                                        <el-progress style="display:block; margin: 0 auto" type="dashboard" :percentage="patientPrecision" width="80" stroke-width="4" :color="colors" >
                                            <template #default="{ percentage }">
                                                <h3 class="percentage-value">{{ percentage }}%</h3>
                                                <h5 class="percentage-label">Precision</h5>
                                            </template>
                                        </el-progress>
                                    </el-row>

                                    <el-row style="text-align:center">
                                        <h5 style="display:block; margin: 5px auto">Model Performance for Patient {{ this.$store.state.patientId }}</h5>
                                    </el-row>
                                </el-col>
                            </el-row>
                        </template>
                        </el-popover>
                    <!-- <el-icon size="25px"><Odometer /></el-icon> -->
                </el-col>
            </el-row>
            <el-divider style="margin-top: 0px;margin-bottom:15px"/>

            <el-skeleton style="width: 100%" :loading="!this.$store.state.predFinish" animated >
                <template #template>
                    <el-skeleton :rows="7" animated style="margin-bottom:15px"/>
                </template>
                <template #default>
                    <div style="overflow: auto; max-height: 80vh" v-infinite-scroll="loadLabel" infinite-scroll-disabled="disabled">
                        <el-row v-for="(cycle,index) in this.cycles" :key="index">
                            <el-text tag="ins" style="font-size:25px;font-weight:10px;margin-bottom:10px">Cycle {{ cycle.cycle }}</el-text>
                        
                            <el-card v-for="(item,index) in cycle.labels" :key="index" shadow="hover" style="border-radius:25px;margin:0px 10px 8px 10px">
                                <el-row>
                                    <el-col :span="3"><el-button text="plain" round
                                        bg @click="locateLabel(item)" style="margin-left: 0;">
                                            <el-text class="mx-1" type="primary" tag="ins">Label {{ item.label_id }}</el-text>
                                    </el-button></el-col>
                                    <el-col :span="20" :offset="1">
                                        <el-form :inline="true" :model="Labels" class="demo-form-inline">
                                            <el-form-item label="Start:" style="margin-left: 1em;">
                                                <el-input-number v-model="item.Start" :placeholder="item.Start" style="width: 70px;" 
                                                :controls="false" :disabled="!item.Confirm" @change="rerun = true"/>
                                                <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                            </el-form-item>
                                            <el-form-item label="End:" style="margin-left: 1em;">
                                                <el-input-number v-model="item.End" :placeholder="item.End" style="width: 70px;" 
                                                :controls="false" :disabled="!item.Confirm" @change="rerun = true"/>
                                                <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                            </el-form-item>
                                            <el-form-item label="Duration:" style="margin-left: 1em;">
                                                <!-- <el-input-number v-model="item.Dur" :placeholder="item.Dur" style="width: 45px;" 
                                                :disabled="true" :controls="false" /> -->
                                                <el-text size="large" class="mx-1" type="warning" tag="ins">{{ item.Dur }}</el-text>
                                                <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                            </el-form-item>
                                            <el-form-item style="margin-left: 1em;">
                                                <el-switch v-model="item.Confirm" :active-icon="CircleCheckFilled" :inactive-icon="CircleCloseFilled" 
                                                style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" size="small" 
                                                active-text="Confirm Event" inactive-text="Discard Event" @change="rerun = true"/>
                                            </el-form-item>
                                            
                                            <!-- <LabelInfoCard :label-id="item.label_id"/> -->
                                        </el-form>
                                    </el-col>
                                </el-row>
                            </el-card>
                            <el-divider style="margin-top: 10px;margin-bottom:15px"/>
                        </el-row>
                        <!-- <el-text class="mx-1" type="warning" style="text-align:center;display:block;margin:auto" v-show="loadingLabel">Loading...</el-text> -->
                        <el-text class="mx-1" type="warning" style="text-align:center;display:block;margin:auto" v-show="noMoreLabel">End of Events</el-text>
                    </div>
                </template>
            </el-skeleton>
            
            <!-- <el-row v-for="(item,index) in [Labels[currentPage - 1]]" :key="index" > -->
            
            <!-- <el-row>
                <el-pagination v-model:current-page="currentPage" :page-size="1"
                layout="prev, pager, next, jumper" :total="labelNum" style="display: flex;margin: auto;"
                @size-change="handleSizeChange" @current-change="handleCurrentChange"/>
            </el-row> -->
            <el-row style="margin-top: 10px;">
                
            </el-row>
        </el-card>
    </el-row>
    
    <div></div>
</template>

<script>
import LabelButton from '@/components/LabelButton.vue'
import LabelInfoCard from '@/components/LabelInfoCard.vue'
import { computed } from "vue"
import axios from 'axios';

export default {
    name: 'BruxismLabel',
    components: {
        LabelButton,
        LabelInfoCard,
    },
    data () {
        return{
            Labels:[],
            labelNum: 0,
            currentPage: 1,
            rerun: false,
            load:false,
            loadingLabel: false,
            count: 3,
            dialogFormVisible: false,
            formLabelWidth: '100px',
            form:{'label_id':'','Start':0,'End':0,'Dur':0},
            colors : [
                { color: '#f56c6c', percentage: 20 },
                { color: '#e6a23c', percentage: 40 },
                { color: '#5cb87a', percentage: 60 },
                { color: '#1989fa', percentage: 80 },
                { color: '#6f7ad3', percentage: 100 },
            ],
            cycles: [],
            // activeLabel: [],
        }
    },
    computed: {
        studyPrecision() {
            if (this.$store.state.studyPrecision == null || this.$store.state.studyPrecision == 0 || this.$store.state.studyPrecision == undefined || this.$store.state.studyPrecision == NaN)
                return '--'
            return this.$store.state.studyPrecision
        },
        patientPrecision() {
            if (this.$store.state.patientPrecision == null || this.$store.state.patientPrecision == 0 || this.$store.state.patientPrecision == undefined || this.$store.state.patientPrecision == NaN)
                return '--'
            return this.$store.state.patientPrecision
        },
        activeLabel() {
            // return JSON.parse(this.$store.state.labels).filter((item) => item.Start<this.$store.state.endPoint && item.End>this.$store.state.startPoint)
            return this.Labels.slice(0,this.count)
        },
        noMoreLabel () {
            return this.count >= this.labelNum
        },
        disabled () {
            return this.loadingLabel || this.noMoreLabel
        }
    },
    methods: {
        confirmLabel(){
            console.log(this.Label)
            const path = 'http://127.0.0.1:5000/label-brux';
            const payload = [];

            for(var i=0; i<this.Labels.length; i++){
                payload.push({
                    "patient_id": this.$store.state.patientId,
                    "week":this.$store.state.week,
                    "night_id":this.$store.state.nightId,
                    "recorder":this.$store.state.recorder,
                    "label_id": this.Labels[i]['label_id'],
                    "location_begin": this.Labels[i]['location_begin'],
                    "location_end": this.Labels[i]['location_end'],
                    "start_index": this.Labels[i]['start_index'],
                    "end_index": this.Labels[i]['end_index'],
                    "Start": this.Labels[i]['Start'],
                    "End": this.Labels[i]['End'],
                    "Confirm": this.Labels[i]['Confirm'],
                })
            };

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            axios.post(path, payload, {headers})
            .then((res) => {
                this.$message({
                    showClose: true,
                    message: 'The above events have been confirmed.',
                    type: 'success'
                });

                console.log(res);
                // this.$store.commit('clearLabels');
                // this.load = false;
                // this.$store.commit('updateBruxLabelKey')
            })
            .catch(err=>{
                console.log(err)
                // this.load = false;
            })
        },
        locateLabel(item){
            this.$store.commit('setLabelRange',{plotStart:0, plotEnd:0});
            this.$store.commit('setEventNo', item.label_id);
            this.$store.commit('updateLinePlotKey');
            // this.$store.commit('setLabelRange',{plotStart:item.Start, plotEnd:item.End});
        },
        openDialog(){
            this.form.Start = this.$store.state.startPoint;
            this.form.End = this.$store.state.endPoint;
            this.dialogFormVisible = true;
        },
        submitNewLable(){
            this.form.label_id = (this.labelNum + 1);
            this.form.Location_begin = this.form.Start * this.$store.state.samplingRate;
            this.form.Location_end = this.form.End * this.$store.state.samplingRate;
            // this.form.Dur = computed(()=>{  return this.form.End - this.form.Start;})
            this.Labels.push(this.form);
            this.Labels[this.labelNum].Confirm = true;
            this.computeDur();
            // this.Labels[this.labelNum].Dur = computed(()=>{  return this.Labels[this.labelNum].End - this.Labels[this.labelNum].Start  })
            // this.labelNum ++;
            console.log(this.Labels);
            console.log(this.labelNum)
            this.$store.commit('saveLabels',JSON.stringify(this.Labels));
            this.$store.commit('setSelectedTimeSpan', { start: this.form.Start, end: this.form.End });
            this.form = {'label_id':'','Start':0,'End':0,'Dur':0};
            this.dialogFormVisible = false;
            this.$store.commit('updateLinePlotKey');
        },
        // handleSizeChange(val){
        //     console.log(`${val} items per page`)
        // },
        // handleCurrentChange(page){
        //     this.currentPage = page;
        //     console.log(`current page: ${this.currentPage}`)
        // },
        loadLabel() {
            this.loadingLabel = true
            setTimeout(() => {
                this.count += 2
                this.loadingLabel = false
            }, 200)
        },
        // TODO: check sampling rate
        computeDur(){
            this.labelNum = 0;
            this.cycles = [];
            this.cycleNum = 0;
            let samplingRate = this.$store.state.samplingRate;
            console.log(samplingRate)
            for (let label in this.Labels){
                // console.log(this.Labels[label])
                this.Labels[label].Start = Math.floor(this.Labels[label].location_begin / samplingRate * 1000) / 1000;
                this.Labels[label].End = Math.floor((this.Labels[label].location_end+1) / samplingRate * 1000) / 1000;
                this.Labels[label].Dur = computed(()=>{  return Math.floor((this.Labels[label].End - this.Labels[label].Start) * 10) / 10 })
                this.Labels[label].Confirm = true
                let cycle = Math.floor(this.Labels[label].Start / 90 / 60) + 1;
                let findCycle = this.cycles.find((item)=>{return item.cycle == cycle});
                if(findCycle){
                    findCycle.labels.push(this.Labels[label]);
                } else {
                    this.cycles.push({'cycle':cycle, 'labels':[this.Labels[label]]});
                    this.cycleNum ++;
                }
                this.labelNum ++;
            }
            console.log(this.Labels);
            console.log(this.cycles);
        },
        async loadWeekImg(){
            const path = `http://127.0.0.1:5000/weekly-sum-img`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };
            let payload = {
                params: {
                    p: this.$store.state.patientId,
                    w: this.$store.state.week,
                }
            };
            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log("week img received");
                    // console.log(res.data);
                    this.$store.commit('getWeekImg', "http://127.0.0.1:5000/weekly-sum-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week);
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        async loadNightImg(){
            const path = `http://127.0.0.1:5000/night-pred-img`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };
            let payload = {
                params: {
                    p: this.$store.state.patientId,
                    w: this.$store.state.week,
                    n: this.$store.state.nightId,
                    r: this.$store.state.recorder
                }
            };
            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log("night img received");
                    // console.log(res.data);
                    this.$store.commit('getNightImg', "http://127.0.0.1:5000/night-pred-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week+'&n='+this.$store.state.nightId+'&r='+this.$store.state.recorder)
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        async loadPredLabels(){
            const path = `http://127.0.0.1:5000/label-brux/${this.$store.state.patientId}/${this.$store.state.week}/${this.$store.state.nightId}/${this.$store.state.recorder}`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };

            await axios.get(path, {headers})
                .then((res) => {
                    console.log("Data received");
                    console.log(res.data);
                    // this.loading = ref(false);
                    this.Labels = res.data;
                    if(!this.Labels||this.Labels.length == 0){
                        this.$notify({
                            duration: 0,
                            title: 'NO EVENTS DETECTED',
                            dangerouslyUseHTMLString: true,
                            message: '<strong>No events detected. Please check the control files, adjust the filter or start with another day to rerun the model.</strong>',
                            type: 'warning'
                        });
                        this.loadNightImg()
                        this.loadWeekImg()
                        this.$store.commit('updateLinePlotKey');
                        return;
                    }
                    // this.$nextTick(() => {
                    this.computeDur();
                    this.$store.commit('saveLabels',JSON.stringify(this.Labels));
                    this.$store.commit('setPredFinish', true);
                    // })
                    this.loadNightImg()
                    this.loadWeekImg()
                    this.$store.commit('updateLinePlotKey');
                    this.$store.commit('updateBruxLabelKey');
                    // return res.data;
                })
                .catch(err=>{
                    console.log(err)
                })
            
        },
        loadAll() {
            return [
                {
                    'label_id': 1,
                    'Start': 5.952,
                    'End': 8.432,
                    // 'Dur': 2.48,
                    'Confirm': true,
                },
                {
                    'label_id': 2,
                    'Start': 9.868,
                    'End': 13.020,
                    // 'Dur': 3.162,
                    'Confirm': true,
                },
                {
                    'label_id': 3,
                    'Start': 15.634,
                    'End': 19.127,
                    // 'Dur': 3.4875,
                    'Confirm': false,
                }
            ]
        },
    },
    // TODO: loading status and sequence
    beforeMount() {
        this.$store.commit('getNightImg','');
        this.$store.commit('getWeekImg', '');
        if(this.$store.state.labels){
            console.log("Labels already loaded")
            this.Labels = JSON.parse(this.$store.state.labels);
            if(!this.Labels||this.Labels.length == 0){
                this.$notify({
                    duration: 0,
                    title: 'NO EVENTS DETECTED',
                    dangerouslyUseHTMLString: true,
                    message: '<strong>No events detected. Please check the control files, adjust the filter or start with another day to rerun the model.</strong>',
                    type: 'warning'
                });
                return;
            }
            console.log(this.Labels);
            this.computeDur();
            this.$store.commit('setPredFinish', true);
            this.loadNightImg()
            this.loadWeekImg()
            // console.log('active label', this.activeLabel)
            // this.$store.commit('clearLabels');

        }else{
            console.log("Labels not loaded")
            this.loadPredLabels();
        }
        this.$store.commit('selectEvent', JSON.stringify(this.Labels[0]))
        // await this.loadPredLabels();
        //   this.submit = computed(()=>{return localStorage.getItem('submit')});
        //   this.rerun = computed(()=>{return localStorage.getItem('rerun')});
    },
}
</script>

<style scoped>
.box-card {
    max-height: calc(97vh)
}
</style>