<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the Bruxism Detection page!</h1>
        </el-col>
    </el-row>
    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=3 />
        </el-col>
    </el-row>
    <el-row style="margin-top: 3%;">
        <el-col :span="7" :offset="5">
            <router-link :to="'/sleep/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Sleep Stage Detection</el-button>
            </router-link>
        </el-col>
        <el-col :span="7" :offset="5">
            <router-link :to="'/treatment/'">
                <el-button type="primary" plain>
                    Treatment Analysis<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
            </router-link>
        </el-col>
    </el-row>
    <el-row style="margin-top: 2em;margin-bottom: 2em;">
        <el-button type="primary" size="large" @click="rerender" style="display: block;margin: 0 auto;">
            Open Weekly Summary
        </el-button>
        <el-dialog v-model="weekSummaryVisible" title="Weekly Summary" center width="60%">
            <TreatHeatMap v-if="isShow"/>
        </el-dialog>
    </el-row>

    <el-row>
        <el-col :span="11" style="padding-left: 1.5em;">
            <el-affix :offset="20">
                <BruxismLabel/>
            </el-affix>
        </el-col>
        <el-col :span="11" :offset="1">
            <LinePlot/>
        </el-col>
    </el-row>

    <!-- <el-row>
        <el-col :span="11">
            <el-row>
                <LinePlot/>
            </el-row>
            <el-row style="margin-top: 30px;">
                <el-col :span="22" :offset="2">
                    <BruxismLabel/>
                </el-col>
            </el-row>
            <el-row style="margin-top: 3%;">
                <el-col :offset="15">
                    <el-button color="#626aef" plain size="large" loading>
                        Rerun Bruxism Classification
                    </el-button>
                </el-col>
            </el-row>
        </el-col>
        <el-col :span="11" :offset="2">
            <TreatHeatMap/>
        </el-col>
    </el-row> -->
</template>


<script>
import Stepper from '@/components/Stepper.vue';
// import DataSpace from '../components/DataSpace.vue'
import LinePlot from '../components/LinePlot.vue'
import TreatHeatMap from '../components/TreatHeatMap.vue'
// import { Orange } from '@element-plus/icons-vue'
import BruxismLabel from '@/components/BruxismLabel.vue';

export default {
    name: 'BruxismPage',
    components: {
        Stepper,
        // DataSpace,
        LinePlot,
        TreatHeatMap,
        BruxismLabel
    },
    data () {
        return {
            weekSummaryVisible: false,
            isShow: true
        }
    },
    methods:{
        rerender(){
            this.weekSummaryVisible = true;
            this.isShow = false;
            this.$nextTick(() => {
                this.isShow = true;
            });
        }
    }
};
</script>