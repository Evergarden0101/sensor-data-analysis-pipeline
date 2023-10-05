<template>

<div class="common-layout">
    <el-container>
      <el-container>
        <el-header>
            <h1 style="text-align: center;">This is the Sleep Stage Detection page!</h1>
            <el-row style="margin-top: 2%;">
                <el-col :span="14" :offset="6">
                   <Stepper step=2 /> 
                </el-col>
                
            </el-row>
            

            <h2 align="center" style="margin-top: 3%;">Patient: {{ this.$store.state.patientId }}, Week: {{ this.$store.state.week }}, Night id: {{ this.$store.state.nightId }}</h2>
            <h3 align="center">Threshold Filtering</h3>
        </el-header>
        <el-main>
            <SleepHeatMap />
        </el-main>
      </el-container>
      <el-aside width="400px" style="margin-top: 18%; margin-right: 3%;"><SleepHeatMapLegend /></el-aside>
    </el-container>
</div>

</template>


<script>
import Stepper from '@/components/Stepper.vue';
import SleepHeatMap from '@/components/SleepHeatMap.vue';
import SleepHeatMapLegend from '@/components/SleepHeatMapLegend.vue'
export default {
    name: 'SleepPage',
    components: {
        Stepper,
        SleepHeatMap,
        SleepHeatMapLegend
    },
};
</script>