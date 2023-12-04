<template>
  <el-alert v-if="!this.$store.state.settingsExist" title="Before starting, please create and save the settings clicking on the top-right button." type="warning" center show-icon/>
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
        <el-tooltip
          class="box-item"
          :disabled="this.$store.state.settingsExist"
          effect="dark"
          content="Please save settings before starting!"
          placement="top-start"
        >
        <el-button type="primary" :disabled="!this.$store.state.settingsExist" plain>Start</el-button>
        </el-tooltip>
      </router-link>
    </el-col>
  </el-row>
</template>

<script>
import Stepper from '../components/Stepper.vue';
import axios from 'axios';
export default {
    name: 'HomePage',
    components: {
      Stepper
    },
    async mounted(){
      this.$store.commit('updateSettingsExist', 0);
      await this.checkExistingSettings();
    },
    methods: {
      async checkExistingSettings(){
        const path = 'http://127.0.0.1:5000/settings-exist/';
        const headers = { 
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        };
        await axios.get(path, {headers})
        .then((res) => {
            this.$store.commit('updateSettingsExist', res.data.settings_exist);
            console.log("ARE SETTINGS SAVED")
            console.log(this.$store.state.settingsExist)
        })
        .catch(err=>{
            console.log(err)
        })
      }
    }
};
</script>