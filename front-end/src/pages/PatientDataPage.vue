<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the Patient Data page!</h1>
        </el-col>
    </el-row>

    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=1 />
        </el-col>
    </el-row>
    <el-row style="margin-top: 2%;">
        <el-col :span="10" :offset="7">
            <h2>Patients data available:</h2>
            <el-table :data="tableData" :default-sort="{ prop: 'patient_id', order: 'ascending' }" @row-dblclick="saveSelectedPatientData" style="width: 100%">
                <el-table-column prop="patient_id" label="Patient ID" sortable width="180" />
                <el-table-column prop="week" label="Week" width="180" />
                <el-table-column prop="night_id" label="Night ID" />
            </el-table>
        </el-col>
    </el-row>


</template>

<script>
import Stepper from '@/components/Stepper.vue';
import axios from 'axios';

export default {
    name: 'PatientDataPage',
    components: {
        Stepper,
    },
    data() {
        return {
            tableData : []
 
    }
    },
    methods: {
        loadAll() {
            const path = 'http://localhost:5000/existing-patients-recordings/';
            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };
            axios.get(path, {headers})
            .then((res) => {
                this.tableData = res.data;
            })
            .catch(err=>{
                console.log(err)
            })

        },
        saveSelectedPatientData(){
            console.log("Double clicked");
        }
    },
    beforeMount(){
        this.loadAll()
    }

};
</script>