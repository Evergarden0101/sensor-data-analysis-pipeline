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
            <el-table :data="tableData"
                      :default-sort="{ prop: 'patient_id', order: 'ascending' }"
                      highlight-current-row
                      @row-dblclick="saveSelectedPatientData" style="width: 100%">
                <el-table-column prop="patient_id" label="Patient ID" sortable width="180" />
                <el-table-column prop="week" label="Week" width="180" />
                <el-table-column prop="night_id" label="Night ID" />
                <el-table-column fixed="right" label="Operations" width="120">
                    <template #default="scope">
                        <el-button
                        link
                        type="primary"
                        size="small"
                        @click.prevent="choosePatient(scope.$index)"
                        >
                        Select
                        </el-button>
                    </template>
                </el-table-column>
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
        async loadAll() {
            const path = 'http://localhost:5000/existing-patients-recordings/';
            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };
            await axios.get(path, {headers})
            .then((res) => {
                this.tableData = res.data;
            })
            .catch(err=>{
                console.log(err)
            })

        },
        saveSelectedPatientData(){
            console.log("Double clicked");
        },
        choosePatient(index){
            console.log(this.tableData[index]);
            this.$store.commit('updatePatientSeletion', this.tableData[index]);
            console.log(this.$store.state);
            this.$router.push('/filtering');

        }
    },
    async beforeMount(){
        await this.loadAll()
    }

};
</script>