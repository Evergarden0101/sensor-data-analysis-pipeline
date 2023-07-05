<template>
    <el-row style="padding-top: 5px;">
      <el-col :span="8">
        <input id="dataset" type="file" style="font-size: 18.5px;">
        <!-- <label id="data" for="param-dataset" data-toggle="tooltip" data-placement="right" title="Tip: upload a new file.">{{ dataset }}</label> -->
        <el-select v-model="dataset" class="m-2" id="selectFile" placeholder="Choose dataset type" :onchange="selectDataSet()" size="large">
          <el-option
            v-for="item in dataTypes"
            :key="item.value"
            :label="item.label"
            :value="item.value"
          />
        </el-select>
      </el-col>
      <el-col :span="8" style="font-size: 18.5px;">
        Data Space (Sorted by Predicted Probability)
      </el-col>
      <!--
      <el-col cols="2">
        <button class="btn-outline-success"
        id="initializeID"
        v-on:click="initialize">
        <font-awesome-icon icon="search" />
        {{ searchText }}
        </button>
        <button class="btn-outline-danger"
        id="resetID"
        v-on:click="reset">
        <font-awesome-icon icon="trash" />
        {{ resetText }}
        </button>
      </el-col>
    -->
    </el-row>
</template>

<script>
import Papa from 'papaparse'
// import { EventBus } from '../main.js'
// import {$,jQuery} from 'jquery';
import * as d3Base from 'd3'
import { sliderBottom } from 'd3-simple-slider'
import mitt from 'mitt'

const d3 = Object.assign(d3Base, { sliderBottom })
const emitter = mitt()

export default {
  name: 'DataSetSlider',
  data () {
    return {
      defaultDataSet: 'EEG', // default value for the first data set
      searchText: 'Feature exploration',
      resetText: 'Factory reset',
      dataset: '',
      dataTypes: [
        {
          value: 'EEG',
          label: 'EEG',
        },
        {
          value: 'ECG',
          label: 'ECG',
        },
        {
          value: 'EMG',
          label: 'EMG',
        },
      ]
    }
  },
  methods: {
    selectDataSet () {   
      const fileName = document.getElementById('selectFile')
      // this.defaultDataSet = fileName.el-options[fileName.selectedIndex].value
      // this.defaultDataSet = this.defaultDataSet.split('.')[0]
      this.defaultDataSet = this.dataset
      
      emitter.emit('SendToServerDataSetConfirmation', this.defaultDataSet);
      d3.select("#data").select("input").remove();
      // this.dataset = "";
      var data;
      d3.select("#dataset")
        .on("change", function() {
          var file = d3.event.target.files[0];
          Papa.parse(file, {
              header: true,
              dynamicTyping: true,
              skipEmptyLines: true,
              complete: function(results) {
                data = results.data;
                emitter.emit('SendToServerLocalFile', data)
              }
            });
        })
    },

    reset () {
      emitter.emit('reset')
      emitter.emit('alternateFlagLock')
    },

    initialize () {
      emitter.emit('ConfirmDataSet')
    },
  },
  mounted () {
  },
}
</script>
