<template>
    <el-row style="margin-bottom: 5%;">
        <el-col>
            <h1 style="text-align: center;">This is the data upload page!</h1>
        </el-col>
    </el-row>

    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=1 />
        </el-col>
    </el-row>

    <el-row style="margin-top: 5%">
        <el-col align-center :span="6" :offset="9">
            <el-form :model="form" label-width="120px">
                <el-form-item label="Patient">
                    <el-select v-model="form.patient" placeholder="Select">
                        <el-option
                            v-for="item in options"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                            :disabled="item.disabled"
                            />
                    </el-select>
                </el-form-item>
                <el-form-item label="Days">
                    <el-select v-model="form.day" placeholder="Select">
                            <el-option
                                    v-for="item in days"
                                    :key="item.value"
                                    :label="item.label"
                                    :value="item.value"
                                    :disabled="item.disabled"
                                />
                    </el-select>
                </el-form-item>
                <el-form-item>
                    <router-link :to="'/sleep/'">
                        <el-button type="primary">Go to sleep stage classification</el-button>
                    </router-link> 
                </el-form-item>
            </el-form>
        </el-col>
    </el-row>
</template>

<script>
import Stepper from '@/components/Stepper.vue';

export default {
    name: 'SelectPatientPage',
    components: {
        Stepper,
    },
    data() {
        return {
            form: {
                patient: '',
                day: ''
            },
            options : [
            {
                value: 'Patient1',
                label: 'Patient 1',
            },
            {
                value: 'Patient2',
                label: 'Patient 2',
                disabled: true,
            },
            {
                value: 'Patient3',
                label: 'Patient3',
                disabled: true
            },
            ],
            days : [
            {
                value: 'Day1',
                label: 'Day 1',
                disabled: true,
            },
            {
                value: 'Day2',
                label: 'Day 2',
                disabled: true,
            },
            {
                value: 'Day3',
                label: 'Day 3'
            },
            ]
        }
    }
};
</script>
  