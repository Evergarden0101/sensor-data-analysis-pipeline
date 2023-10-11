<template>
    <el-row style="margin-bottom: 3%;">
        <el-col>
            <h1 style="text-align: center;">This is the Treatment Analysis page!</h1>
        </el-col>
    </el-row>
    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=4 />
        </el-col>
    </el-row>
    <el-row style="margin-top: 3%;">
        <el-col :span="18" :offset="6">
            <router-link :to="'/events-classification/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Events Classification</el-button>
            </router-link>
        </el-col>
    </el-row>

    <el-row style="margin-top: 3%;">
        <el-col :offset="10">
            <el-radio-group v-model="radio1" size="large">
                <el-radio-button label="Day" />
                <el-radio-button label="Week" />
                <el-radio-button label="Month" />
            </el-radio-group>
        </el-col>
    </el-row>

    <div style="margin-top: 3%;">
        <div v-if="radio1==='Day'" style="text-align: center;">
            Day
        </div>

        <div v-if="radio1==='Week'" style="text-align: center;">
            Week
        </div>

        <div v-if="radio1==='Month'" style="text-align: center;">
            Month
        </div>
    </div>

    <div style="border-style: solid; border-color: black; border-width:3px; padding: 40px; text-align: center; width:50%; margin: auto;">
        <el-button>
            Add patient
        </el-button>
    </div>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
import { ref } from 'vue';

export default {
    name: 'TreatmentPage',
    components: {
        Stepper,

    },
    data(){
        return{
            radio1: ref('Week')
        }
    }
};
</script>