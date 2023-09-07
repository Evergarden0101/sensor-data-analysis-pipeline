<template>
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
    <el-form v-if="!error" :model="form" label-width="120px">
        <p><b>General information</b></p>
        <el-form-item label="Type of study" required="true">
            <el-select v-model="form.studyType" class="m-2" placeholder="Select" size="large">
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
            <el-select v-model="form.activityType" class="m-2" placeholder="Select" size="large">
                <el-option
                v-for="item in activities"
                :key="item.value"
                :label="item.label"
                :value="item.value"
                :disabled="item.disabled"
                />
            </el-select>
        </el-form-item>

        <p><b>Sensor data information</b></p>

        <el-form-item label="Sensor types" required="true">
            <el-select
                v-model="form.sensorsTypes"
                multiple
                placeholder="Select"
                style="width: 240px"
                >
                <el-option
                    v-for="item in sensorsList"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value"
                    :disabled="item.disabled"
                />
                </el-select>
        </el-form-item>
        <div v-if="form.sensorsTypes.length >0">
            <p><i>Number of channels</i></p>
        
        
            <div v-for="n in form.sensorsTypes.length">
                <el-form-item :label="form.sensorsTypes[n-1]" required="true">
                    <el-input-number v-model="form.channels[form.sensorsTypes[n-1]]" :min="1" :max="5" :disabled="true"/>
                </el-form-item>
            </div>
        </div>
        <p><i>Sampling rates</i></p>
                <el-form-item label="Original" required="true">
                        <el-input-number v-model="form.originalSampling" :min="120" :max="2000" />
                </el-form-item>

                <div v-if="form.studyType=='sleep' && form.activityType=='bruxism'">
                    <el-form-item label="REM" required="true">
                        <el-input-number v-model="form.REMSampling" :min="120" :max="1000" />
                    </el-form-item>

                    <el-form-item label="NREM" required="true">
                        <el-input-number v-model="form.NREMSampling" :min="120" :max="256" />
                    </el-form-item>
                </div>

                

        <p><b>Dataset information</b></p>

        <el-form-item label="Data file format" required="true">
            <el-select v-model="form.fileFormat" class="m-2" placeholder="Select" size="large">
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
                v-model="form.filtered"
                active-text="Yes"
                inactive-text="No">
            </el-switch>
        </el-form-item>

        <el-form-item v-if="form.filtered" label="Normalized" required="true">
            <el-switch
                v-model="form.normalized"
                active-text="Yes"
                inactive-text="No">
            </el-switch>
        </el-form-item>
        
        <div v-if="form.sensorsTypes.length > 0" >
            <p><i>Channel names on .csv file</i></p>

            <el-form-item label="ECG channel" v-if="form.sensorsTypes.includes('ECG')" required="true">
            <el-input v-model="form.ecgChannelName" placeholder="Please input" /> 
            </el-form-item>

            <el-form-item label="EMG channel 1" v-if="form.sensorsTypes.includes('EMG')" required="true">
            <el-input v-model="form.emgChannel1Name" placeholder="Please input" /> 
            </el-form-item>

            <el-form-item label="EMG channel 2" v-if="form.sensorsTypes.includes('EMG')" required="true">
            <el-input v-model="form.emgChannel2Name" placeholder="Please input" /> 
            </el-form-item>

            <el-form-item label="EMG channel 3" v-if="form.sensorsTypes.includes('EMG')" required="true">
            <el-input v-model="form.emgChannel3Name" placeholder="Please input" /> 
            </el-form-item>
        </div>
        
        <el-form-item>
        <el-button type="primary" @click="onSubmit">Save</el-button>
        </el-form-item>
    </el-form>
</template>



<script>
import { reactive } from 'vue';
import { ref } from 'vue';
import axios from 'axios';

export default {
    name: 'SettingsForm',
    data() {
        return {
            form: reactive({
                studyType: ref(''),
                activityType: ref(''),
                sensorsTypes: ref(["ECG", "EMG"]),
                originalSampling: ref(2000),
                REMSampling: ref(1000),
                NREMSampling: ref(256),
                filtered: true,
                normalized: true,
                fileFormat: ref('csv'),
                channels: {
                    "ECG": ref(1),
                    "EMG": ref(3)
                },
                ecgChannelName: ref(''),
                emgChannel1Name: ref(''),
                emgChannel2Name: ref(''),
                emgChannel3Name: ref('')
            }),
            error: false,

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
    methods: {
        onSubmit(){
            
            if(this.form.studyType != '' && this.form.activityType != '' && this.form.sensorsTypes != [] && this.form.fileFormat != '' && this.form.ecgChannelName != '' && this.form.emgChannel1Name != '' && this.form.emgChannel2Name != '' && this.form.emgChannel3Name != ''){
                console.log('submit!');
                console.log(this.form)
                this.postSettings();
                this.postSensors();
            }
            else{
                this.setError();
            } 
        },

        postSettings(){
            console.log(this.form.studyType)

            const path = 'http://localhost:5000/settings/';

            const payload = {
                "studyType": this.form.studyType,
                "activityType": this.form.activityType,
                "originalSampling": this.form.originalSampling,
                "REMSampling": this.form.REMSampling,
                "NREMSampling": this.form.NREMSampling,
                "fileFormat": this.form.fileFormat,
                "filtered": this.form.filtered,
                "normalized": this.form.normalized
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
            })
        },
        postSensors(){
            console.log(this.form.studyType)

            const path = 'http://localhost:5000/sensors/';

            const payload = [
                {
                    "type": "ECG",
                    "name": this.form.ecgChannelName
                }, {
                    "type": "EMG",
                    "name": this.form.emgChannel1Name
                }, {
                    "type": "EMG",
                    "name": this.form.emgChannel2Name
                }, {
                    "type": "EMG",
                    "name": this.form.emgChannel3Name
                }
            ];


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
            })
        },
        setError(){
            this.error = !this.error;
        }
    }

};
</script>