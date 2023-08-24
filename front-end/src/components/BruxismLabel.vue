<template>
    <el-row>
        <el-card class="box-card" style="border: solid 1px;border-radius: 10px; width: 100%; margin-left: auto;margin-right: auto;">
            <h3 align="center" style="margin-bottom: 30px;">Bruxism Event Predictions</h3>
            <el-row v-for="(item,index) in Labels" :key="index" style="margin-bottom: 10px;">
                <el-col :span="3"><h5>{{ item.id }}</h5></el-col>
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
                    style="margin-left: 1em;--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" size="small" 
                    active-text="Confirm Bruxism" inactive-text="Not Bruxism" @change="rerun = true"/>
                </el-form>
                </el-col>
                <el-divider />
            </el-row>
            <el-button type='primary' text='primary' @click="dialogFormVisible = true" style="margin-top: -15px;">
                Add Bruxism Event
            </el-button>
            <el-dialog v-model="dialogFormVisible" title="Add Bruxism Event" center width="30%" align-center draggable>
                <el-form :model="form">
                <el-form-item label="Start Time:" :label-width="formLabelWidth">
                    <el-input-number v-model="form.Start" style="width: 70px; margin-left: 20px;"  :controls="false" />
                        <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                </el-form-item>
                <el-form-item label="End Time:" :label-width="formLabelWidth">
                    <el-input-number v-model="form.End" style="width: 70px;margin-left: 20px;"  :controls="false" />
                        <el-text size="large" style="margin-left: 0.3em;">s</el-text>
                </el-form-item>
                </el-form>
                <template #footer>
                <span class="dialog-footer">
                    <el-button @click="dialogFormVisible = false">Cancel</el-button>
                    <el-button type="primary" @click="dialogFormVisible = false">
                    Confirm
                    </el-button>
                </span>
                </template>
            </el-dialog>
            <LabelButton :labels="Labels" style="display: block;margin: 15px auto 5px auto;"/>
        </el-card>
    </el-row>
    <el-row style="margin-top: 3em;">
        <h5 style="display: block;margin: auto;">Change at least 1 label to rerun classifier</h5>
    </el-row>
    <el-row style="margin-top: 1em;">
        <el-button color="#626aef" plain size="large" :disabled="!rerun" style="display: block;margin: 0 auto;" 
        @click="load = true" :loading="load">
            Rerun Bruxism Classification
        </el-button>
    </el-row>
</template>

<script>
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import LabelButton from '@/components/LabelButton.vue'
import { computed } from "vue"
export default {
    name: 'BruxismLabel',
    components: {
        LabelButton,
    },
    data () {
        return{
            Labels:[],
            rerun: false,
            load:false,
            dialogFormVisible: false,
            formLabelWidth: '100px',
            form:{'id':'','Start':'','End':''}
        }
    },
    methods: {
        // changeInput(e) {
        //     if (e.toString().indexOf('.') >= 0) {
        //         e = e.toString().substring(0, e.toString().indexOf('.') + 4);
        //     }
        // },
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
      }
      console.log(this.Labels)
    },
}
</script>
