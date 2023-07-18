<template>
    <Stepper step="3"/>
    <h1 style="margin: 50px 0px;"> This is the Bruxism Detection Page!</h1>
    <!-- <DataSpace/> -->
    <el-row>
        <el-col :span="11">
            <el-row>
                <LinePlot/>
            </el-row>
            <el-row>
                <el-card class="box-card" style="margin-top: 80px; border: solid 1px;border-radius: 10px; width: 400px; margin-left: auto;margin-right: auto;">
                    <p align="center">Labeling</p>
                    <p>label 1: xxxxx</p>
                    <p>label 2: xxxxx</p>
                </el-card>
            </el-row>
            <el-row>
                <el-button color="#626aef" :dark="TRUE" plain style="margin-top: 80px; margin-left: auto;margin-right: auto;" size="large" :icon="Orange" loading>
                    Rerun Bruxism Classification</el-button>
            </el-row>
        </el-col>
        <el-col :span="11" :offset="2">
            <TreatHeatMap/>
        </el-col>
    </el-row>

    <router-link :to="'/treatment/'" style="margin-right: 20px;">
        <el-button>Treatment Analysis</el-button> 
    </router-link>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
// import DataSpace from '../components/DataSpace.vue'
import LinePlot from '../components/LinePlot.vue'
import TreatHeatMap from '../components/TreatHeatMap.vue'
import { Orange } from '@element-plus/icons-vue'
export default {
name: 'BruxismPage',
components: {
    Stepper,
    // DataSpace,
    LinePlot,
    TreatHeatMap,
},
};
</script>