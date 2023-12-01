<template>
<h1 style="text-align: center;"><el-icon :size="default"><Filter /></el-icon> Filtering</h1>
<h2 style="text-align: center;">Sleep Stage Detection</h2>
<el-row style="margin-bottom: 1%;">
    <el-col align-center :span="16" :offset="4">
        <Stepper step=2 />
    </el-col>
</el-row>

<div class="common-layout">
    <el-container>
      <el-container>
        <el-header style="margin-bottom: 2%;">
                <h2 align="center" style="margin-top: 3%; text-align: center;">Patient: {{ this.$store.state.patientId }}, Week: {{ this.$store.state.week }}, Night id: {{ this.$store.state.nightId }}</h2>
        </el-header>
        <el-main>
            <SleepHeatMap />
        </el-main>
      </el-container>
      <el-aside width="400px" style="margin-top: 7%; margin-right: 3%;"><SleepHeatMapLegend /></el-aside>
    </el-container>
</div>

</template>


<script>
import Stepper from '@/components/Stepper.vue';
import SleepHeatMap from '@/components/SleepHeatMap.vue';
import SleepHeatMapLegend from '@/components/SleepHeatMapLegend.vue'
export default {
    name: 'FilteringPage',
    components: {
        Stepper,
        SleepHeatMap,
        SleepHeatMapLegend
    },
};
</script>