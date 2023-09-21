<template>
    <el-row>
        <el-card class="box-card" style="border: solid 1px;border-radius: 10px; width: 100%; margin-left: auto;margin-right: auto;">
            <h3 align="center" style="margin-bottom: 30px;">Events Predictions</h3>
            <!-- <el-row v-for="(item,index) in [Labels[currentPage - 1]]" :key="index" > -->
            <el-row v-for="(item,index) in Labels" :key="index" >
                <el-col :span="3"><el-button text="plain" type="" bg @click="locateLabel(item)" style="border-radius: 8px;"><el-link>{{ item.id }}</el-link></el-button></el-col>
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
                        <LabelInfoCard/>
                    </el-form>
                    
                </el-col>
                <el-divider />
            </el-row>
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
    <el-row style="margin-top: 3em;">
        <h5 style="display: block;margin: auto;">Change at least 1 label to rerun classifier</h5>
    </el-row>
    <el-row style="margin-top: 1em;">
        <LabelButton :disabled="!rerun" :labels="Labels" color="#626aef" plain size="large"
            style="display: block;margin: 0 auto"/>

        <!-- <el-button  plain size="large" :disabled="!rerun" style="display: block;margin: 0 auto;" 
        @click="load = true" :loading="load">
            Rerun Bruxism Classification
        </el-button> -->
    </el-row>
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
            dialogFormVisible: false,
            formLabelWidth: '100px',
            form:{'id':'','Start':0,'End':0},
        }
    },
    methods: {
        locateLabel(item){
            this.$store.commit('updateLinePlotKey');
            this.$store.commit('setLabelRange',{labelStart:item.Start, labelEnd:item.End});
        },
        openDialog(){
            this.form.Start = this.$store.state.startPoint;
            this.form.End = this.$store.state.endPoint;
            this.dialogFormVisible = true;
        },
        submitNewLable(){
            this.form.id = 'Label ' + (this.labelNum + 1);
            this.Labels.push(this.form);
            this.labelNum ++;
            this.form = {'id':'','Start':0,'End':0};
            this.dialogFormVisible = false;
        },
        handleSizeChange(val){
            console.log(`${val} items per page`)
        },
        handleCurrentChange(page){
            this.currentPage = page;
            console.log(`current page: ${this.currentPage}`)
        },
        loadAll() {
            return [
                {
                    'id': 'Label 1',
                    'Start': 5.952,
                    'End': 8.432,
                    // 'Dur': 2.48,
                    'Confirm': true,
                },
                {
                    'id': 'Label 2',
                    'Start': 9.868,
                    'End': 13.020,
                    // 'Dur': 3.162,
                    'Confirm': true,
                },
                {
                    'id': 'Label 3',
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
        for (let label in this.Labels){
            // console.log(this.Labels[label])
            this.Labels[label].Dur = computed(()=>{  return this.Labels[label].End - this.Labels[label].Start  })
            this.labelNum ++;
        }
        //   this.submit = computed(()=>{return localStorage.getItem('submit')});
        //   this.rerun = computed(()=>{return localStorage.getItem('rerun')});
    },
}
</script>
