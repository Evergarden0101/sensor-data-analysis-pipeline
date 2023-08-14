<template>
  <el-row style="margin-bottom: 10%; margin-top: 5%;">
    <el-col>
      <h1 style="text-align: center;">Welcome to the sensor data pipeline for the labelling and monitoring of bruxism events!</h1>
    </el-col>
  </el-row>
  <el-row>
    <el-col align-center :span="12" :offset="6">
      <Stepper step=0 />
    </el-col>
  </el-row>
  <el-row  style="margin-top: 10%;">
    <el-col :offset="11" :span="2">
      <!--
      <router-link :to="'/upload/'">
        <el-button type="primary" plain>Start</el-button>
      </router-link>
      -->
      <router-link :to="'/select-patient/'">
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