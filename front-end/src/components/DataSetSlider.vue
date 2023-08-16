<template>
  <el-card class="box-card" style="padding-top: 5px; border: solid 1px;border-radius: 10px; display: block;margin: auto;">
    <!--
    <el-row >
       <label id="data" for="param-dataset" data-toggle="tooltip" data-placement="right" title="Tip: upload a new file.">{{ dataset }}</label>
      <el-select v-model="dataset" class="m-2" id="selectFile" placeholder="Choose dataset type" :onchange="selectDataSet()" size="large" style="margin-left: auto;margin-right: auto;">
        <el-option
          v-for="item in dataTypes"
          :key="item.value"
          :label="item.label"
          :value="item.value"
        />
      </el-select>
      
       <p style="font-size: 16px;">Dataset</p>
    </el-row>
    -->
    <el-row>
      <!-- TODO: action for upload address -->
      <!-- :before-upload="beforeFileUpload"-->
      <el-upload
        class="upload-demo"
        drag
        action="https://jsonplaceholder.typicode.com/posts/"
        multiple
        :limit="2"
        :file-list="fileList"
        :on-exceed="handleExceed"
        :before-remove="beforeRemove"
        style="margin-left: auto;margin-right: auto;margin-top: 40px;margin-bottom: 30px;">
        <i class="el-icon-upload"></i>
        <div class="el-upload__text" style="font-size: 18px;">Drag files here, or <em>click to upload</em></div>
        <div class="el-upload__tip" slot="tip" style="font-size: 15px;">Please upload a CSV file</div>
      </el-upload>
    </el-row>
  </el-card>
</template>

<script>
import Papa from 'papaparse'
import * as d3 from 'd3'
import mitt from 'mitt'
import { ElMessage, ElMessageBox } from 'element-plus'

// const d3 = Object.assign(d3Base, { sliderBottom })
const emitter = mitt()

export default {
  name: 'DataSetSlider',
  data () {
    return {
      defaultDataSet: 'EEG', // default value for the first data set
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
      ],
      fileList: [],
    }
  },
  methods: {
    beforeFileUpload(file) {
      const isCSV = file.type === 'text/csv';
      // const isLt2M = file.size / 1024 / 1024 < 2;

      if (!isCSV) {
        ElMessage({
          showClose: true,
          duration:0,
          message: 'Only CSV files can be uploaded!',
          type: 'error',
        });
      }
      // if (!isLt2M) {
      //   this.$message.error('File size cannot exceed 2MB!');
      // }
      return isJPG;
    },
    handleExceed(files, fileList) {
      ElMessage({
          showClose: true,
          duration:0,
          message: 'Only 2 files are allowed to upload at a time.',
          type: 'warning',
        });
      // this.$message.warning(`Only 2 files are allowed at a time, currently ${files.length} files are selected, ${files.length + fileList.length} files in total.`);
    },
    beforeRemove(file, fileList) {
      return ElMessageBox.confirm(`Cancel the transfer of ${file.name} ?`)
    },
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
        .on("change", function(event) {
          var file = event.target.files[0];
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

    // reset () {
    //   emitter.emit('reset')
    //   emitter.emit('alternateFlagLock')
    // },

    // initialize () {
    //   emitter.emit('ConfirmDataSet')
    // },
  },
  mounted () {
  },
}
</script>
