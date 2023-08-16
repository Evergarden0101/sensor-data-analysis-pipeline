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
    <el-row style="margin-top: 5%;">
        <TreatHeatMap />
    </el-row>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
import TestButton from '@/components/TestButton.vue';
import TreatHeatMap from '../components/TreatHeatMap.vue'
export default {
    name: 'TreatmentPage',
    components: {
        Stepper,
        TestButton,
        TreatHeatMap,
    },
};
</script>