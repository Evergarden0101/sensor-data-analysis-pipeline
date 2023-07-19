<template>
    <router-link :to="'/'">
        <el-button type="primary" @click="postLabel">Home</el-button>
    </router-link>
</template>

<script>
import axios from 'axios';
export default{
    name: 'HomeButton',
    methods:  {
        postLabel(){
            const path = 'http://localhost:5000/label-brux';
            const payload = {
                "location_begin": 6474,
                "location_end": 7890,
                "duration": 678.8
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
    }
}
</script>