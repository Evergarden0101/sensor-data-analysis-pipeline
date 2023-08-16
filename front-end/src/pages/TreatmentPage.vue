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
    <p style="text-align: center; margin-top: 2%;">Please select a patient id and a day:</p>
    <el-row style="margin-top: 1%;">
        <el-col :span="2" :offset="10">
            <el-select v-model="value1" filterable placeholder="Patient id">
                <el-option
                v-for="item in options"
                :key="item.value1"
                :label="item.label"
                :value="item.value1"
                :disabled="item.disabled"
                />
            </el-select>
        </el-col>
        <el-col :span="12">
            <el-select v-model="value2" filterable placeholder="Day">
                <el-option
                v-for="item in days"
                :key="item.value2"
                :label="item.label"
                :value="item.value2"
                :disabled="item.disabled"
                />
            </el-select>
        </el-col>
    </el-row>
    <div v-if="value2">
        <el-row v-if="value2" style="margin-top: 4%;">
            <el-col :span="9" :offset="3">
                <TreatmentHeatMap />
            </el-col>
            <el-col :span="12">
                <TreatmentHeatMap />
            </el-col>
        </el-row>
        <el-row v-if="value2">
            <el-col :span="9" :offset="3">
                <TreatmentHeatMap />
            </el-col>
            <el-col :span="12">
                <TreatmentHeatMap />
            </el-col>
        </el-row>
    </div>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
import TestButton from '@/components/TestButton.vue';
import TreatmentHeatMap from '../components/TreatmentHeatMap.vue';
import { ref } from 'vue';

export default {
    name: 'TreatmentPage',
    components: {
        Stepper,
        TestButton,
        TreatmentHeatMap,
    },
    data() {
        return{
            value1: ref(''),
            value2: ref(''),
            options : [
            {
                value1: 'Patient1',
                label: 'Patient 1',
            },
            {
                value1: 'Patient2',
                label: 'Patient 2',
                disabled: true,
            },
            {
                value1: 'Patient3',
                label: 'Patient3',
                disabled: true
            },
            ],
            days : [
            {
                value2: 'Day1',
                label: 'Day 1',
                disabled: true,
            },
            {
                value2: 'Day2',
                label: 'Day 2',
                disabled: true,
            },
            {
                value2: 'Day3',
                label: 'Day 3'
            },
            ]
        }
    }
};
</script>