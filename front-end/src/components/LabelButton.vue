<template>
    <el-button @click="postLabel" :loading="load">Rerun Events Classification</el-button>
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
        postLabel(){
            this.load = true;
            const path = 'http://127.0.0.1:5000/label-brux';
            const payload = [];

            for(var i=0; i<this.labels.length; i++){
                payload.push({
                    "patient_id": this.$store.state.patientId,
                    "week":this.$store.state.week,
                    "night_id":this.$store.state.nightId,
                    "label_id": this.labels[i]['label_id'],
                    "location_begin": this.labels[i]['Start'],
                    "location_end": this.labels[i]['End'],
                    "corrected": true,
                })
            };

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            // axios.post(path, payload, {headers})
            // .then((res) => {
            //     console.log(res);
            //     this.$store.commit('clearLabels');
            //     // this.load = false;
            //     this.$store.commit('updateStudyAccuracy', '--');
            //     this.$store.commit('updatePatientAccuracy', '--');
            //     // this.$store.commit('updateBruxLabelKey')
            // })
            // .catch(err=>{
            //     console.log(err)
            //     // this.load = false;
            // })
        }
    },
}
</script>