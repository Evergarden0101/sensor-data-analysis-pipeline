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
            <router-link :to="'/bruxism/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Events Detection</el-button>
            </router-link>
        </el-col>
    </el-row>
    <p style="text-align: center; margin-top: 2%;">Please select a patient id to visualize mutiple weekly summary:</p>
    <el-row style="margin-top: 1%;">
        <el-col :offset="10">
            <el-form :model="form" label-width="100px">
                <el-form-item label="Patient UID">
                    <el-autocomplete
                        v-model="form.patientId"
                        :fetch-suggestions="querySearch"
                        clearable
                        class="inline-input w-50"
                        placeholder="Input Patient UID"
                        @select="handleSelect"
                        style="overflow: visible;"
                    >
                        <template #default="{ item }">
                        <span
                            style="
                            float: left;
                            font-size: 15px;
                            "
                            >{{ item.id }}</span>
                        <span style="color: var(--el-text-color-secondary);float: right">UID</span>
                        </template>
                    </el-autocomplete>
                </el-form-item>
            </el-form>
        </el-col>
    </el-row>
    <div v-if="form.patientId">
        <el-row style="margin-top: 4%;" class="row-bg" justify="space-evenly">
            <el-col :span="7">
                <TreatHeatMapW1 />
            </el-col>
            <el-col :span="7">
                <TreatHeatMapW2 />
            </el-col>
            <el-col :span="7">
                <TreatHeatMapW3 />
            </el-col>
        </el-row>
    </div>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
import TestButton from '@/components/TestButton.vue';
import TreatHeatMapW2 from '../components/TreatHeatMapW2.vue';
import TreatHeatMapW1 from '@/components/TreatHeatMapW1.vue';
import TreatHeatMapW3 from '@/components/TreatHeatMapW3.vue';

export default {
    name: 'TreatmentPage',
    components: {
        Stepper,
        TestButton,
        TreatHeatMapW2,
        TreatHeatMapW1,
        TreatHeatMapW3

    },
    data() {
        return {
            form: {
                patientId: '',
                day: '',
            },
            ids:[],
            props : { expandTrigger: 'hover'},
            days : [{
                value: 'Week1',
                label: 'Week 1',
                children: [
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
                ]},
                {
                value: 'Week2',
                label: 'Week 2',
                children: [
                {
                    value: 'Day1',
                    label: 'Day 1',
                },
                {
                    value: 'Day2',
                    label: 'Day 2',
                    disabled: true,
                },
                {
                    value: 'Day3',
                    label: 'Day 3',
                    disabled: true,
                },
            ]}
            ],
        }
    },
    methods: {
      onSubmit() {
        console.log(this.form.patientId);
        console.log(this.form.day);
      },
      handleChange(value) {
        console.log(value)
      },
      handleSelect(item) {
        console.log(item);
        this.form.patientId = item.id;
      },
      querySearch(queryString, cb) {
        var ids = this.ids;
        var results = queryString ? ids.filter(this.createFilter(queryString)) : ids;
        // call callback function to return suggestions
        cb(results);
      },
      createFilter(queryString) {
        return (id) => {
          return (id.id.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
        };
      },
      loadAll() {
        return [
          { "id": "1111111" },
          { "id": "2222222" },
          { "id": "3333333" },
          { "id": "4444444" },
          { "id": "5555555" },
          { "id": "6666666" },
          { "id": "7777777" }
         ];
      },
    },
    beforeMount() {
      this.ids = this.loadAll();
    }
};
</script>