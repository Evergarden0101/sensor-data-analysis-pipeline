<template>
    <h1> This is the Sleep Stage Classification Page!</h1>
    <el-row style="margin-bottom: 5%;">
        <el-column :span="24"  align-center>
            <Stepper step=2 />
        </el-column>
    </el-row>

    <el-row>
        <router-link :to="'/bruxism/'" style="margin-right: 20px;">
            <el-button>Bruxism Detection</el-button>  
        </router-link>
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