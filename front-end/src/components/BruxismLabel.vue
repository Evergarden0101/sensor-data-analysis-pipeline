<template>
    <el-card class="box-card" style="border: solid 1px;border-radius: 10px; width: 100%; margin-left: auto;margin-right: auto;">
        <p align="center">Labeling</p>
        <el-row v-for="(item,index) in Labels" :key="index" style="margin-bottom: 20px;">
            <el-col :span="4"><h5>{{ item.id }}</h5></el-col>
            <el-col :span="20">
                <el-form :inline="true" :model="Labels" class="demo-form-inline">
                <el-form-item label="Start:" style="margin-left: 1em;">
                    <el-input-number v-model="item.Start" :placeholder="item.Start" style="width: 65px;" 
                    :controls="false" />
                </el-form-item>
                <el-form-item label="End:" style="margin-left: 1em;">
                    <el-input-number v-model="item.End" :placeholder="item.End" style="width: 65px;" 
                    :controls="false" />
                </el-form-item>
                <el-form-item label="Duration:" style="margin-left: 1em;">
                    <el-input-number v-model="item.Dur" :placeholder="item.Dur" style="width: 65px;" 
                    :disabled="true" :controls="false" />
                </el-form-item>
                <el-switch v-model="item.Confirm" :active-icon="CircleCheckFilled" :inactive-icon="CircleCloseFilled" 
                style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" size="small"
                active-text="Confirm Bruxism" inactive-text="Not Bruxism"/>
            </el-form>
            </el-col>
            <el-divider />
        </el-row>
        <el-button type='primary' text='primary' @click="dialogFormVisible = true">
            Add Bruxism Event
        </el-button>
        <el-dialog v-model="dialogFormVisible" title="Add Bruxism Event" center width="30%" align-center draggable>
            <el-form :model="form">
            <el-form-item label="Start Time" :label-width="formLabelWidth">
                <el-input-number v-model="form.Start" style="width: 70px; margin-left: 20px;"  :controls="false" />
            </el-form-item>
            <el-form-item label="End Time" :label-width="formLabelWidth">
                <el-input-number v-model="form.End" style="width: 70px;margin-left: 20px;"  :controls="false" />
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
        <LabelButton/>
    </el-card>
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
    }
}
</script>