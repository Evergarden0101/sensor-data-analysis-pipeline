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

    <!-- <div class="hp-icons-container"> -->
        <el-row style="margin-top: 50px;">
            <el-col :span="4" :offset="10">
                <DataSetSlider/>
            </el-col>
        </el-row>

        <el-row>
            <el-col :offset="10">
                <DataSetInfo style="margin-top: 20px;"/>
            </el-col>
        </el-row>

        

        <!--
        <el-row style="margin-top: 50px;">
            <router-link :to="'/sleep/'" style="margin-right: 20px;">
                <el-button>Sleep Stage Classification</el-button>  
            </router-link>
        </el-row>
        -->
        
    <!-- </div> -->
</template>

<script>
import Stepper from '@/components/Stepper.vue';
import DataSetSlider from '../components/DataSetSlider.vue'
import DataSetInfo from '@/components/DataSetInfo.vue';
export default {
    name: 'DataUploadPage',
    components: {
        DataSetSlider,
        Stepper,
        DataSetInfo
    },
};
</script>
  