<!-- eslint-disable no-import-assign -->
<template>
    <b-row style="padding-top: 5px;">
      <b-col cols="2" style="margin-left: -35px">
        <label id="data" for="param-dataset" data-toggle="tooltip" data-placement="right" title="Tip: upload a new file.">{{ dataset }}</label>
        <select id="selectFile" @change="selectDataSet()">
            <option value="eeg.csv" selected>EEG</option>
            <option value="ecg.csv" >ECG</option>
            <option value="emg.csv" >EMG</option>
        </select>
      </b-col>
      <b-col cols="8">
        Data Space (Sorted by Predicted Probability)
      </b-col>
      <!--
      <b-col cols="2">
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
      </b-col>
    -->
    </b-row>
</template>

<script>
import Papa from 'papaparse'
import { EventBus } from '../main.js'
// import {$,jQuery} from 'jquery';
import * as d3Base from 'd3'
import { sliderBottom } from 'd3-simple-slider'

// attach all d3 plugins to the d3 library
// eslint-disable-next-line no-import-assign
const d3 = Object.assign(d3Base, { sliderBottom })

export default {
  name: 'DataSetSlider',
  data () {
    return {
      defaultDataSet: 'EEG', // default value for the first data set
      searchText: 'Feature exploration',
      resetText: 'Factory reset',
      dataset: 'Data set'
    }
  },
  methods: {
    selectDataSet () {   
      const fileName = document.getElementById('selectFile')
      this.defaultDataSet = fileName.options[fileName.selectedIndex].value
      this.defaultDataSet = this.defaultDataSet.split('.')[0]

      if (this.defaultDataSet == "EEG" || this.defaultDataSet == "ECG" || this.defaultDataSet == "EMG") { // This is a function that handles a new file, which users can upload.
        this.dataset = "Data set"
        d3.select("#data").select("input").remove(); // Remove the selection field.
        // EventBus.$emit('SendToServerDataSetConfirmation', this.defaultDataSet)
      } else {
        // EventBus.$emit('SendToServerDataSetConfirmation', this.defaultDataSet)
        d3.select("#data").select("input").remove();
        this.dataset = ""
        var data
        d3.select("#data")
          .append("input")
          .attr("type", "file")
          .style("font-size", "18.5px")
          .style("width", "200px")
          .on("change", function() {
            var file = d3.event.target.files[0];
            Papa.parse(file, {
                header: true,
                dynamicTyping: true,
                skipEmptyLines: true,
                complete: function(results) {
                  data = results.data;
                  EventBus.$emit('SendToServerLocalFile', data)
                }
              });
          })
      }
    },
    reset () {
      EventBus.$emit('reset')
      EventBus.$emit('alternateFlagLock')
    },
    initialize () {
      EventBus.$emit('ConfirmDataSet')
    },
  },
  mounted () {
  },
}
</script>
