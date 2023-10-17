<template>
    <div v-if="settingsPosted">
        <el-alert title="Settings saved successfully." type="success" center show-icon />
    </div>    
    <div v-if="error">
        <el-dialog v-model="error" width="30%" center>
        <span>
            <el-result
            icon="error"
            title="Error"
            sub-title="Please fill in all the mandatory fields."
        >
            <template #extra>
                <el-button type="primary" @click="setError()" plain>Back</el-button>
            </template>
        </el-result>
        </span>
    </el-dialog>
    </div>

    <div v-if="!error">

    <div v-if="formNumber === 1">
        <el-form :model="generalInfoForm" label-width="120px">
            <p><b>General information</b></p>
            <el-form-item label="Type of study" required="true">
                <el-select v-model="generalInfoForm.studyType" class="m-2" placeholder="Select" size="large">
                    <el-option
                    v-for="item in studyTypes"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                    :disabled="item.disabled"
                    />
                </el-select>
            </el-form-item>

            <el-form-item label="Activity to detect" required="true">
                <el-select v-model="generalInfoForm.activityType" class="m-2" placeholder="Select" size="large">
                    <el-option
                    v-for="item in activities"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                    :disabled="item.disabled"
                    />
                </el-select>
            </el-form-item>
        </el-form>

        <el-button type="primary" @click="handleNext1()" style="margin-top:3%">Next<el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
    </div>

    <div v-if="formNumber === 2">
        <el-form :model="sensorsForm" label-width="120px" style="margin-top: 3%;">
            <p><b>Sensor data information</b></p>
            <el-row>
                <el-col :offset="14" :span="10">
                    Number of channels
                </el-col>
            </el-row>
            <div v-for="(sensor, index) in sensorsForm" :key="index">
                <el-row>
                <el-form-item :label="getSensorLabel(index.charAt(6))">
                    <el-col :span="8">
                        <el-select
                            v-model="sensor.type"
                            placeholder="Type"
                            >
                                <el-option
                                    v-for="item in sensorsList"
                                    :key="item.value"
                                    :label="item.label"
                                    :value="item.value"
                                    :disabled="item.disabled"
                                />
                            </el-select>
                    </el-col>

                    <el-col :offset="2" :span="8">
                        <el-input-number placeholder="#Channels" v-model="sensor.channels" :min="1" :max="5" />
                    </el-col>
                    <el-col v-if="index.charAt(6) >1" :offset="2" :span="4">
                        <el-button type="danger" circle @click="removeSensor(index)">
                            <el-icon>
                                <Delete />
                            </el-icon>
                        </el-button>
                    </el-col>

                </el-form-item>
                </el-row>    
            </div>
            <el-row>
                <el-col :offset="1">
                    <el-button @click="addSensor()" >
                        <el-icon><Plus /></el-icon> Add sensor
                    </el-button>
                </el-col>
            </el-row>
        </el-form>

        <el-button-group  style="margin-top:3%">
            <el-button type="primary" @click="formNumber--"><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Previous</el-button>
            <el-button type="primary" @click="handleNext2()">Next<el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
        </el-button-group>
    </div>

    <div v-if="formNumber === 3">
        <p><b>Sampling rates</b></p>
            <el-form :model="samplingRateForm">
                <el-form-item label="Original (Hz)" required="true">
                        <el-input-number v-model="samplingRateForm.originalSampling" :min="120" :max="2000" />
                </el-form-item>

                <div v-if="generalInfoForm.studyType=='sleep' && generalInfoForm.activityType=='bruxism'">
                    <el-form-item label="Selected ranges (Hz)" required="true">
                        <el-input-number v-model="samplingRateForm.SelectedSampling" :min="120" :max="1000" />
                    </el-form-item>

                    <el-form-item label="Non selected ranges (Hz)" required="true">
                        <el-input-number v-model="samplingRateForm.NonSelectedSampling" :min="100" :max="256" />
                    </el-form-item>
                </div>
            </el-form>

        <el-button-group  style="margin-top:3%">
            <el-button type="primary" @click="formNumber--"><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Previous</el-button>
            <el-button type="primary" @click="formNumber++">Next<el-icon class="el-icon--right"><ArrowRight /></el-icon></el-button>
        </el-button-group>
    </div>

    <div v-if="formNumber === 4">
        <el-form :model="datasetInfoForm">
            <p><b>Dataset information</b></p>

            <el-form-item label="Data file format" required="true">
                <el-select v-model="datasetInfoForm.fileFormat" class="m-2" placeholder="Select" size="large">
                    <el-option
                    v-for="item in fileFormats"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                    :disabled="item.disabled"
                    />
                </el-select>
            </el-form-item>

            <el-form-item label="Filtered" required="true">
                <el-switch
                    v-model="datasetInfoForm.filtered"
                    active-text="Yes"
                    inactive-text="No">
                </el-switch>
            </el-form-item>

            <el-form-item v-if="datasetInfoForm.filtered" label="Normalized" required="true">
                <el-switch
                    v-model="datasetInfoForm.normalized"
                    active-text="Yes"
                    inactive-text="No">
                </el-switch>
            </el-form-item>

            <p><i>Data path</i></p>
            <el-form-item label="Full data path">
                <el-input v-model="datasetInfoForm.dataPath" placeholder="Please input the full data path" style="width:400px" /> 
            </el-form-item>
            
            <p><i>Channel names on .csv file</i></p>
            <div v-for="(channels,type) in datasetInfoForm.channelsNames" :key="type">
                <div v-for="(name,channel) in channels" :key="channel">
                    <el-form-item :label="getChannelNameLabel(type, channel.charAt(7))" required="true">
                    <el-input v-model="datasetInfoForm.channelsNames[type][channel]" placeholder="Please input" /> 
                </el-form-item>
                    
                </div>

            </div>
            <el-button type="primary" @click="formNumber--"><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Previous</el-button>
            <el-button @click="saveSettings()">Save</el-button>
        </el-form>

    </div>
    </div>

</template>



<script>
import { reactive } from 'vue';
import { ref } from 'vue';
import axios from 'axios';

export default {
    name: 'SettingsForm',
    data() {
        return {
            settings: {},
            sensors: [],
            error: false,
            dbEntryExist: false,
            settingsPosted: false,
            formNumber: ref(1),
            sensorsList: [
                {
                    value: 'ECG',
                    label: 'ECG',
                },
                {
                    value: 'EMG',
                    label: 'EMG',
                },
                {
                    value: 'eog',
                    label: 'EOG',
                    disabled: true
                },
                {
                    value: 'eeg',
                    label: 'EEG',
                    disabled: true
                }
            ],

            sensorsNumber: ref(1),

            generalInfoForm: reactive({
                studyType: ref(''),
                activityType: ref(''),
            }),

            sensorsForm: reactive({
                sensor1 : {type: ref(''), channels: ref('')},
            }),

            samplingRateForm: reactive({
                originalSampling: ref(2000),
                SelectedSampling: ref(1000),
                NonSelectedSampling: ref(256),
            }),

            datasetInfoForm: reactive({
                filtered: true,
                normalized: true,
                fileFormat: ref('csv'),
                channelsNames: ref({}),
                dataPath : ref('')
            }),
            studyTypes: [
                {
                    value: 'sleep',
                    label: 'Sleep'
                },
                {
                    value: 'emotion',
                    label: 'Emotion recognition',
                    disabled: true,
                },
                {
                    value: 'cardiac',
                    label: 'Cardiac',
                    disabled: true
                }

            ],
            activities: [
                {
                    value: 'bruxism',
                    label: 'Bruxism'
                },
                {
                    value: 'emotion',
                    label: 'Emotion',
                    disabled: true,
                },
                {
                    value: 'arythmia',
                    label: 'Arythmia',
                    disabled: true
                }

            ], 
            sensorsList: [
                {
                    value: 'ECG',
                    label: 'ECG',
                },
                {
                    value: 'EMG',
                    label: 'EMG',
                },
                {
                    value: 'eog',
                    label: 'EOG',
                    disabled: true
                },
                {
                    value: 'eeg',
                    label: 'EEG',
                    disabled: true
                }
            ],
            fileFormats: [
                {
                    value: 'csv',
                    label: '.csv',
                },
                {
                    value: 'txt',
                    label: '.txt',
                    disabled: true
                }
            ]
        }
    },
    async mounted(){
        await this.getSettings();
        await this.getSensors();

    
        if(Object.keys(this.settings).length > 0 && Object.keys(this.sensors).length > 0){
            this.dbEntryExist = true;
            this.generalInfoForm.studyType = this.settings.study_type;
            this.generalInfoForm.activityType = this.settings.activity;
            this.samplingRateForm.originalSampling = this.settings.original_sampling;
            this.samplingRateForm.SelectedSampling = this.settings.selected_sampling;
            this.samplingRateForm.NonSelectedSampling = this.settings.non_selected_sampling;
            this.samplingRateForm.fileFormat = this.settings.dataset_format;
            this.datasetInfoForm.dataPath = this.settings.data_path;

            if(this.settings.normalized == 1){
                this.datasetInfoForm.normalized = true;
            } else {
                this.datasetInfoForm.normalized = false;
            }

            if(this.settings.filtered == 1){
                this.datasetInfoForm.filtered = true;
            } else {
                this.datasetInfoForm.filtered = false;
            }

            // Get all sensor data

            let sensorsGrouped = this.sensors.reduce(function(sums,entry){
                sums[entry.type] = (sums[entry.type] || 0) + 1;
                return sums;
            },{});

            let count = 1

            for (const key in sensorsGrouped) {
                let sensorName = "sensor" + count
                
                this.sensorsForm[sensorName] = { type: key, channels: sensorsGrouped[key]}
                this.datasetInfoForm.channelsNames[key] = {};
                
                count ++;
            }

            this.sensorsNumber = count - 1;

            for (const key in this.sensors){
                let count = Object.keys(this.datasetInfoForm.channelsNames[this.sensors[key]['type']]).length + 1
                let channelName = "channel" + count
    
                this.datasetInfoForm.channelsNames[this.sensors[key]['type']][channelName] = this.sensors[key]['name']
            }
        }
    },

    methods: {
        handleNext1(){
            if(this.generalInfoForm.studyType != '' && this.generalInfoForm.activityType != ''){
                this.formNumber++
            }
            else{
                this.setError();
            }
        },
        handleNext2(){
            let error = false;
            for(let i=0; i<Object.keys({...this.sensorsForm}).length; i++){
                if(this.sensorsForm[Object.keys(this.sensorsForm)[i]]['type'] === ''){
                    error = true;
                }
            }

            if(error){
                this.setError();
            }

            else{
               this.formNumber ++; 
               //This would force to show the entries from DB (not a good idea if the values are changed)
               /*
                if(!this.dbEntryExist){
                    this.datasetInfoForm.channelsNames = this.getChannelsInputs({...this.sensorsForm});
               }
               */
               this.datasetInfoForm.channelsNames = this.getChannelsInputs({...this.sensorsForm});
            }    
        },
        getChannelNameLabel(channel, id){
            return channel + " Sensor " + id;
        },  

        postSettings(){
            const path = 'http://localhost:5000/settings/';

            const payload = {
                "studyType": this.generalInfoForm.studyType,
                "activityType": this.generalInfoForm.activityType,
                "originalSampling": this.samplingRateForm.originalSampling,
                "SelectedSampling": this.samplingRateForm.SelectedSampling,
                "NonSelectedSampling": this.samplingRateForm.NonSelectedSampling,
                "fileFormat": this.datasetInfoForm.fileFormat,
                "filtered": this.datasetInfoForm.filtered,
                "normalized": this.datasetInfoForm.normalized,
                "dataPath": this.datasetInfoForm.dataPath
            };

            this.$store.commit('updateSamplingRate', this.samplingRateForm.originalSampling);

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            axios.post(path, payload, {headers})
            .then((res) => {
                console.log(res);
                this.settingsPosted = true;
            })
            .catch(err=>{
                console.log(err)
                this.settingsPosted = false;
            })
        },
        postSensors(){
            const path = 'http://localhost:5000/sensors/';

            let payload = [];

            for(let i=0; i<Object.keys(this.datasetInfoForm.channelsNames).length; i++){
                let type = Object.keys(this.datasetInfoForm.channelsNames)[i];
                let channels = Object.keys(this.datasetInfoForm.channelsNames[Object.keys(this.datasetInfoForm.channelsNames)[i]]);

                for(let j=0; j<channels.length; j++){
                    let channel = Object.keys(this.datasetInfoForm.channelsNames[Object.keys(this.datasetInfoForm.channelsNames)[i]])[j];
                    let channelName = this.datasetInfoForm.channelsNames[type][channel];
                    
                    payload.push({
                        "type": type,
                        "name": channelName.toUpperCase()
                    })
                }
            };

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            axios.post(path, payload, {headers})
            .then((res) => {
                console.log(res);
            })
            .catch(err=>{
                console.log(err)
                this.settingsPosted = false;
            })
        },
        setError(){
            this.error = !this.error;
        },
        getSensorLabel(index){
            return "Sensor " + index  
        },
        async getSettings(){
            const path = 'http://localhost:5000/settings/';

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            await axios.get(path, {headers})
            .then((res) => {
                console.log(res.data);
                this.settings = res.data;
            })
            .catch(err=>{
                console.log(err)
            })
        },
        async getSensors(){

            const path = 'http://localhost:5000/sensors/';

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            await axios.get(path, {headers})
            .then((res) => {
                console.log(res.data);
                this.sensors = res.data;
            })
            .catch(err=>{
                console.log(err)
            })
        },
        addSensor(){
            this.sensorsNumber ++;
            const sensorName = "sensor"+this.sensorsNumber;
            this.sensorsForm[sensorName] = {'type': ref(''), 'channels': ref('')};

        },
        removeSensor(sensorName){
            if(this.sensorsNumber > 1){
                this.sensorsNumber --;
                delete this.sensorsForm[sensorName]; 
            }

        },
        getObjectKey(obj, value) {
            return Object.keys(obj).find(key => obj[key] === value);
        },
        getChannelsInputs(sensorsForm){
            let channelsInputs = {};

            for (const key in sensorsForm){
                channelsInputs[sensorsForm[key]['type']] = {};
            }

            for (const key in sensorsForm){
                for(let i=0; i< sensorsForm[key]['channels']; i++){
                    let channelName = "channel" + (Object.keys(channelsInputs[sensorsForm[key]['type']]).length +1)
                    channelsInputs[sensorsForm[key]['type']][channelName] = "" 
                }
            }
            return channelsInputs;  
        },
        saveSettings(){
            //add check to see if sensors names are not ''
            let error = false;
            for(let i=0; i<Object.keys(this.datasetInfoForm.channelsNames).length; i++){
                let type = Object.keys(this.datasetInfoForm.channelsNames)[i];
                let channels = Object.keys(this.datasetInfoForm.channelsNames[Object.keys(this.datasetInfoForm.channelsNames)[i]]);

                for(let j=0; j<channels.length; j++){
                    let channel = Object.keys(this.datasetInfoForm.channelsNames[Object.keys(this.datasetInfoForm.channelsNames)[i]])[j];
                    let channelName = this.datasetInfoForm.channelsNames[type][channel];

                    if(channelName === ''){
                        error = true;
                    }
                }
            }

            if(error){
                this.setError();
            }

            else{
                console.log("Success")
                this.postSettings();
                this.postSensors();
                this.formNumber = 1;
            }   
        }
    }

};
</script>