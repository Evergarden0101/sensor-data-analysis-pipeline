<template>
  <el-row style="margin-bottom: 10%; margin-top: 5%;">
    <el-col>
      <h1 style="text-align: center;">Human Centered Sensor Data Analysis Pipeline</h1>
    </el-col>
  </el-row>
  <el-row>
    <el-col align-center :span="16" :offset="4">
      <Stepper step=0 />
    </el-col>
  </el-row>
  <el-row  style="margin-top: 10%;">
    <el-col :offset="11" :span="2">
      <!--
      <router-link :to="'/patient/'">
        <el-button type="primary" plain>Start</el-button>
      </router-link>
      -->
      <router-link :to="'/patient-data/'">
        <el-button type="primary" plain>Start</el-button>
      </router-link>
    </el-col>
  </el-row>
</template>

<script>
import Stepper from '../components/Stepper.vue';
export default {
    name: 'HomePage',
    components: {
      Stepper
    },
};
</script>