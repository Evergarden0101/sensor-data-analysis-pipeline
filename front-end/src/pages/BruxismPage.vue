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
    <!-- <DataSpace/> -->
    <el-row>
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
    </el-row>
    <el-row>
        <el-col :offset="11" :span="2" style="margin-top: 20px;">
            <router-link :to="'/treatment/'" style="margin-right: 20px;">
                <el-button>Treatment Analysis</el-button> 
            </router-link>
        </el-col>
    </el-row>
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
        }
    },
};
</script>