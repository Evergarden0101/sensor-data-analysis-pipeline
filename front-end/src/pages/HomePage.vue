<template>
    <h1>This is the Home Page</h1>
    <div class="hp-icons-container">
        <router-link :to="'/eeg-meg/'">
            <button>EEG/MEG DATA</button>  
        </router-link>
        
        <router-link :to="'/ecg/'">
            <button>ECG DATA</button> 
        </router-link>
    </div>
    <DataSetSlider/>
    <!-- <DataSpace/> -->
  </template>
  
  <script>
import DataSetSlider from '../components/DataSetSlider.vue'
// import DataSpace from '../components/DataSpace.vue'
// import * as d3Base from 'd3'

// attach all d3 plugins to the d3 library
// const d3 = Object.assign(d3Base)

export default {
    name: 'HomePage',
    components: {
    DataSetSlider,
    // DataSpace,
    },
};
  </script>
  