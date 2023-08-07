<template>
    <el-card class="box-card" style="border: solid 1px;border-radius: 10px; width: 100%; margin-left: auto;margin-right: auto;">
        <p align="center">Labeling</p>
        <el-row v-for="(item,index) in Labels" :key="index" style="margin-bottom: 20px;border-bottom: solid;">
            <el-col :span="3"><h5>{{ item.id }}</h5></el-col>
            <el-col :span="21">
                <el-form :inline="true" :model="Labels" class="demo-form-inline">
                <el-form-item label="Start:" style="margin-left: 1em;">
                    <el-input v-model="item.Start" :placeholder="item.Start" style="width: 60px;"/>
                </el-form-item>
                <el-form-item label="End:" style="margin-left: 1em;">
                    <el-input v-model="item.End" :placeholder="item.End" style="width: 60px;"/>
                </el-form-item>
                <el-form-item label="Duration:" style="margin-left: 1em;">
                    <el-input v-model="item.Dur" :placeholder="item.Dur" style="width: 60px;" :disabled="true"/>
                </el-form-item>
                <el-switch v-model="item.Confirm" :active-icon="CircleCheckFilled" :inactive-icon="CircleCloseFilled" 
                style="--el-switch-on-color: #13ce66; --el-switch-off-color: #ff4949" size="small"
                active-text="Confirm Bruxism" inactive-text="Not Bruxism"/>
            </el-form>
            </el-col>
        </el-row>
        <LabelButton/>
    </el-card>
</template>

<script>
import { CircleCheckFilled, CircleCloseFilled } from '@element-plus/icons-vue'
import LabelButton from '@/components/LabelButton.vue'
export default {
    name: 'BruxismLabel',
    components: {
        LabelButton,
    },
    data () {
        return{
            Labels:[{
            'id': 'Label 1',
            'Start': 5.952,
            'End': 8.432,
            'Dur': 2.48,
            'Confirm': true,
            },
            {
                'id': 'Label 2',
                'Start': 9.868,
                'End': 13.020,
                'Dur': 3.162,
                'Confirm': true,
            },
            {
                'id': 'Label 3',
                'Start': 15.634,
                'End': 19.127,
                'Dur': 3.4875,
                'Confirm': false,
            }
        ]
        }
        
  },
}
</script>