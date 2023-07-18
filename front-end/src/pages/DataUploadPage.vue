<template>
    <h2>This is the Data Upload Page</h2>

    <el-row>
        <Stepper step="1" />
    </el-row>

    <!-- <div class="hp-icons-container"> -->
        <el-row style="margin-top: 50px;">
            <DataSetSlider/>
        </el-row>

        <DataSetInfo style="margin-top: 20px;"/>

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
  