<template>
    <el-row>
        <el-card class="box-card" style="border: solid 1px;border-radius: 10px; width: 100%; margin-left: auto;margin-right: auto; padding:0">
            <h3 align="center" style="margin-bottom: 20px;margin-top:-5px">Events Predictions</h3>
            <!-- <el-row v-for="(item,index) in [Labels[currentPage - 1]]" :key="index" > -->
            <div style="overflow: auto; max-height: 400px" v-infinite-scroll="loadLabel" infinite-scroll-disabled="disabled">
                <el-row v-for="(item,index) in activeLabel.slice(0,count)" :key="index">
                        <el-col :span="3"><el-button text="plain" type="" bg @click="locateLabel(item)" style="border-radius: 8px;"><el-link>Label {{ item.id }}</el-link></el-button></el-col>
                        <el-col :span="21">
                            <el-form :inline="true" :model="Labels" class="demo-form-inline">
                                <el-form-item label="Start:" style="margin-left: 1em;">
                                    <el-input-number v-model="item.Start" :placeholder="item.Start" style="width: 65px;" 
                                    :controls="false" :disabled="!item.Confirm" @change="rerun = true"/>
                                    <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                </el-form-item>
                                <el-form-item label="End:" style="margin-left: 1em;">
                                    <el-input-number v-model="item.End" :placeholder="item.End" style="width: 65px;" 
                                    :controls="false" :disabled="!item.Confirm" @change="rerun = true"/>
                                    <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                </el-form-item>
                                <el-form-item label="Duration:" style="margin-left: 1em;">
                                    <el-input-number v-model="item.Dur" :placeholder="item.Dur" style="width: 65px;" 
                                    :disabled="true" :controls="false" />
                                    <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                                </el-form-item>
                                <el-switch v-model="item.Confirm" :active-icon="CircleCheckFilled" :inactive-icon="CircleCloseFilled" 
                                style="margin-left: 1em;margin-right: 2em;--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" size="small" 
                                active-text="Confirm Event" inactive-text="Discard Event" @change="rerun = true"/>
                                <LabelInfoCard :label-id="item.id"/>
                            </el-form>
                        </el-col>
                        <el-divider style="margin-top: 0px;margin-bottom:15px"/>
                </el-row>
                <el-text class="mx-1" type="warning" style="text-align:center;display:block;margin:auto" v-if="loadingLabel">Loading...</el-text>
                <el-text class="mx-1" type="warning" style="text-align:center;display:block;margin:auto" v-if="noMoreLabel">End of Events</el-text>
            </div>
            <!-- <el-row>
                <el-pagination v-model:current-page="currentPage" :page-size="1"
                layout="prev, pager, next, jumper" :total="labelNum" style="display: flex;margin: auto;"
                @size-change="handleSizeChange" @current-change="handleCurrentChange"/>
            </el-row> -->
            <el-row style="margin-top: 10px;">
                <el-button type='primary' text='primary' @click="openDialog" style="margin-top: -15px;">
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
            </el-row>
        </el-card>
    </el-row>
    <el-row style="margin-top: 1em;">
        <h5 style="display: block;margin: auto;">Comfirm the above events to rerun classifier</h5>
    </el-row>
    <el-row style="margin-top: 1em;">
        <LabelButton :labels="Labels" color="#626aef" plain size="large"
            style="display: block;margin: 0 auto"/>

        <!-- <el-button  plain size="large" :disabled="!rerun" style="display: block;margin: 0 auto;" 
        @click="load = true" :loading="load">
            Rerun Bruxism Classification
        </el-button> -->
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
    <div></div>
</template>

<script>
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import LabelButton from '@/components/LabelButton.vue'
import LabelInfoCard from '@/components/LabelInfoCard.vue'
import { computed } from "vue"

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
            form:{'id':'','Start':0,'End':0,'Dur':0},
            colors : [
                { color: '#f56c6c', percentage: 20 },
                { color: '#e6a23c', percentage: 40 },
                { color: '#5cb87a', percentage: 60 },
                { color: '#1989fa', percentage: 80 },
                { color: '#6f7ad3', percentage: 100 },
            ],
            studyAccuracy: 80.23,
            patientAccuracy: 80.23,
        }
    },
    computed: {
        activeLabel() {
            return this.Labels.filter((item) => item.Start<this.$store.state.endPoint && item.End>this.$store.state.startPoint)
        },
        noMoreLabel () {
            return this.count >= this.activeLabel.length
        },
        disabled () {
            return this.loading || this.noMoreLabel
        }
    },
    methods: {
        locateLabel(item){
            this.$store.commit('updateLinePlotKey');
            this.$store.commit('setLabelRange',{plotStart:item.Start, plotEnd:item.End});
        },
        openDialog(){
            this.form.Start = this.$store.state.startPoint;
            this.form.End = this.$store.state.endPoint;
            this.dialogFormVisible = true;
        },
        submitNewLable(){
            this.form.id = (this.labelNum + 1);
            // this.form.Dur = computed(()=>{  return this.form.End - this.form.Start;})
            this.Labels.push(this.form);
            this.Labels[this.labelNum].Confirm = true;
            this.computeDur();
            // this.Labels[this.labelNum].Dur = computed(()=>{  return this.Labels[this.labelNum].End - this.Labels[this.labelNum].Start  })
            // this.labelNum ++;
            this.$store.commit('saveLabels',JSON.stringify(this.Labels));
            this.form = {'id':'','Start':0,'End':0,'Dur':0};
            this.dialogFormVisible = false;
            this.$store.commit('updateLinePlotKey');
        },
        handleSizeChange(val){
            console.log(`${val} items per page`)
        },
        handleCurrentChange(page){
            this.currentPage = page;
            console.log(`current page: ${this.currentPage}`)
        },
        loadLabel() {
            this.loadingLabel = true
            setTimeout(() => {
                this.count += 2
                this.loadingLabel = false
            }, 2000)
        },
        computeDur(){
            this.labelNum = 0;
            for (let label in this.Labels){
                // console.log(this.Labels[label])
                this.Labels[label].Dur = computed(()=>{  return this.Labels[label].End - this.Labels[label].Start  })
                this.labelNum ++;
            }
        },
        loadAll() {
            return [
                {
                    'id': 1,
                    'Start': 5.952,
                    'End': 8.432,
                    // 'Dur': 2.48,
                    'Confirm': true,
                },
                {
                    'id': 2,
                    'Start': 9.868,
                    'End': 13.020,
                    // 'Dur': 3.162,
                    'Confirm': true,
                },
                {
                    'id': 3,
                    'Start': 15.634,
                    'End': 19.127,
                    // 'Dur': 3.4875,
                    'Confirm': false,
                }
            ]
        },
    },
    beforeMount() {
        this.Labels = this.loadAll();
        this.computeDur();
        this.$store.commit('saveLabels',JSON.stringify(this.Labels));
        //   this.submit = computed(()=>{return localStorage.getItem('submit')});
        //   this.rerun = computed(()=>{return localStorage.getItem('rerun')});
    },
}
</script>
