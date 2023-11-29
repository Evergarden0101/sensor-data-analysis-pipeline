<template>
    <el-button @click="postLabel" :loading="load">Rerun Model</el-button>
</template>

<script>
import axios from 'axios';
export default{
    name: 'LabelButton',
    props: ['labels'],
    data(){
        return{
            load: false,
        }
    },
    methods:  {
        async loadWeekImg(){
            const path = `http://127.0.0.1:5000/weekly-sum-img`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };
            let payload = {
                params: {
                    p: this.$store.state.patientId,
                    w: this.$store.state.week,
                }
            };
            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log("week img received");
                    // console.log(res.data);
                    this.$store.commit('getWeekImg', "http://127.0.0.1:5000/weekly-sum-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week);
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        async loadNightImg(){
            const path = `http://127.0.0.1:5000/night-pred-img`
            const headers = {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET',
                    'Access-Control-Max-Age': "3600",
                    'Access-Control-Allow-Credentials': "true",
                    'Access-Control-Allow-Headers': 'Content-Type'
            };
            let payload = {
                params: {
                    p: this.$store.state.patientId,
                    w: this.$store.state.week,
                    n: this.$store.state.nightId,
                    r: this.$store.state.recorder
                }
            };
            await axios.get(path, payload, {headers})
                .then((res) => {
                    console.log("night img received");
                    // console.log(res.data);
                    this.$store.commit('getNightImg', "http://127.0.0.1:5000/night-pred-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week+'&n='+this.$store.state.nightId+'&r='+this.$store.state.recorder)
                })
                .catch(err=>{
                    console.log(err)
                })
        },
        // TODO: rurun model, refresh image and plots and heatmap
        postLabel(){
            this.load = true;
            const path = `http://127.0.0.1:5000/rerun-model/${this.$store.state.patientId}/${this.$store.state.week}/${this.$store.state.nightId}/${this.$store.state.recorder}`;
            // const payload = [];

            // for(var i=0; i<this.labels.length; i++){
            //     payload.push({
            //         "patient_id": this.$store.state.patientId,
            //         "week":this.$store.state.week,
            //         "night_id":this.$store.state.nightId,
            //         "label_id": this.labels[i]['label_id'],
            //         "location_begin": this.labels[i]['Start'],
            //         "location_end": this.labels[i]['End'],
            //         "corrected": true,
            //     })
            // };

            // this.$store.commit('getNightImg', '');
            // this.$store.commit('getWeekImg', '');

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            axios.get(path, {headers})
            .then((res) => {
                this.$message({
                    showClose: true,
                    message: 'Model rerun successfully!',
                    type: 'success'
                });
                console.log(res);
                // this.$store.commit('clearLabels');
                this.load = false;

                // TODO: update accuracy
                this.$store.commit('updateStudyPrecision', res.data['study_accuracy']['precision']);
                this.$store.commit('updatePatientPrecision', res.data['patient_accuracy']['precision']);
                this.$message({
                    showClose: true,
                    message: 'Model rerun successed!',
                    type: 'success'
                });
                this.losadNightImg();
                this.loadWeekImg();
                // this.$store.commit('updateBruxLabelKey')
            })
            .catch(err=>{
                console.log(err)
                this.$message({
                    showClose: true,
                    message: 'Error occured in Model rerun!',
                    type: 'error'
                });
                this.load = false;
            })
        }
    },
}
</script>