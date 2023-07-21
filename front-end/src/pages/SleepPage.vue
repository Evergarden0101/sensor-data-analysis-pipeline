<template>
    <el-row style="margin-bottom: 5%;">
        <el-col>
            <h1 style="text-align: center;">This is the Sleep Stage Classification page!</h1>
        </el-col>
    </el-row>
    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=2 />
        </el-col>
    </el-row>

    <el-row>
        <el-col :offset="11" style="margin-top: 5%;">
            <router-link :to="'/bruxism/'" style="margin-right: 20px;">
                <el-button>Bruxism Detection</el-button>  
            </router-link>
        </el-col>
    </el-row>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
export default {
    name: 'SleepPage',
    components: {
        Stepper,
    },
};
</script>