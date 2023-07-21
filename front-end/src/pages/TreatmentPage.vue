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
</template>


<script>
import Stepper from '@/components/Stepper.vue';
export default {
    name: 'TreatmentPage',
    components: {
        Stepper,
    },
};
</script>