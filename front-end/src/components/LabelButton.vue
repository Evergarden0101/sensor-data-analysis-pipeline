<template>
    <el-button type="primary" @click="postLabel">Submit Labels</el-button>
</template>

<script>
import axios from 'axios';
export default{
    name: 'LabelButton',
    props: ['labels'],
    methods:  {
        postLabel(){
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
            })
            .catch(err=>{
                console.log(err)
            })
        }
    },
}
</script>