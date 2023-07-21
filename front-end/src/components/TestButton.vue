<template>
    <el-button @click="getLabel" type=primary>Get data of patient 123</el-button>
    <p v-if="info">{{ info }}</p>
</template>

<script>
import axios from 'axios';
export default{
    name: "TestButton",
    data () {
        return {
            info: null
        }
    },
    methods: {
        getLabel(){
            const path = 'http://localhost:5000/label-brux/123';
            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };
            axios.get(path, {headers})
            .then((res) => {
                this.info = res.data
            })
            .catch(err=>{
                console.log(err)
            })

        }
    }
}
</script>