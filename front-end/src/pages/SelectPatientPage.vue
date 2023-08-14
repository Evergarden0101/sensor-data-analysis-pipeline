<template>
    <el-row style="margin-bottom: 5%;">
        <el-col>
            <h1 style="text-align: center;">This is the data upload page!</h1>
        </el-col>
    </el-row>

    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=1 />
        </el-col>
    </el-row>

    <el-row style="margin-top: 5%">
        <el-col :span="12" :offset="6" align-center>
            <router-link :to="'/sleep/'">
                <el-button type="primary">
                    Patient 1 - Day 3
                </el-button>
            </router-link>
        </el-col>
    </el-row>
</template>

<script>
import Stepper from '@/components/Stepper.vue';

export default {
    name: 'SelectPatientPage',
    components: {
        Stepper,
    },
};
</script>
  