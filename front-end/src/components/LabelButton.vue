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
            const path = 'http://localhost:5000/label-brux';
            const payload = [];

            for(var i=0; i<this.labels.length; i++){
                payload.push({
                    "patient": 123,
                    "location_begin": this.labels[i]['Start'],
                    "location_end": this.labels[i]['End'],
                    "duration": this.labels[i]['End'] - this.labels[i]['Start'] 
                })
            };

            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };

            axios.post(path, payload, {headers})
            .then((res) => {
                console.log(res);
                this.load = false;
            })
            .catch(err=>{
                console.log(err)
            })
        }
    },
}
</script>