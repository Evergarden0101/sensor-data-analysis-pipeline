<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the patient info page!</h1>
        </el-col>
    </el-row>

    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=1 />
        </el-col>
    </el-row>

    <el-row style="margin-top: 3%;">
        <el-col :span="10" :offset="7">
            <el-tabs tab-position="top" style="display: block;margin: auto;" class="demo-tabs" type="border-card">
                <el-tab-pane label="Existing Patient">
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
                        <el-form-item label="Day">
                            <el-cascader :options="days" v-model="form.day" :props="props"
                                @change="handleChange" style="width: 172px"
                                placeholder="Select recorded day" clearable />
                        </el-form-item>
                    </el-form>
                    <el-col :span="22" :offset="1">
                        <el-collapse>
                            <el-collapse-item name="1">
                                <template #title>
                                    <el-icon class="header-icon" style="color: dodgerblue;margin-right: 5px;"><Plus/></el-icon>
                                    <el-text class="mx-1" type="primary">Add new data</el-text>
                                </template>
                                <el-row style="margin-top: 20px;">
                                    <DataSetSlider/>
                                </el-row>
                                <el-row>
                                        <DataSetInfo style="margin-top: 20px;"/>
                                </el-row>
                            </el-collapse-item>
                        </el-collapse>
                    </el-col>
                    <router-link :to="'/sleep/'">
                        <el-button type="primary" plain @click="onSubmit" style="display: block;margin: 30px auto 0 auto;">Confirm</el-button>  
                    </router-link>
                
                </el-tab-pane>
                <el-tab-pane label="New Patient">
                    <b style="font-size: 18px;text-align: center;display: block;margin: auto;">Add new data to start</b>
                    <el-row style="margin-top: 20px;">
                            <DataSetSlider/>
                    </el-row>

                    <el-row>
                            <DataSetInfo style="margin-top: 20px;"/>
                    </el-row>
                    <router-link :to="'/sleep/'">
                        <el-button type="primary" plain @click="onSubmit" style="display: block;margin: 10px auto 0 auto;">Confirm</el-button>  
                    </router-link>
                </el-tab-pane>
            </el-tabs>
        </el-col>
    </el-row>
    

    <!-- <div class="hp-icons-container"> -->
        <!--
        <el-row style="margin-top: 50px;">
            <router-link :to="'/sleep/'" style="margin-right: 20px;">
                <el-button>Sleep Stage Classification</el-button>  
            </router-link>
        </el-row>
        -->
        
    <!-- </div> -->
</template>

<script>
import Stepper from '@/components/Stepper.vue';
import DataSetSlider from '../components/DataSetSlider.vue'
import DataSetInfo from '@/components/DataSetInfo.vue';
export default {
    name: 'PatientInfoPage',
    components: {
        DataSetSlider,
        Stepper,
        DataSetInfo
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
<style>
.demo-tabs > .el-tabs__content {
  padding: 32px;
  /* color: #6b778c; */
  font-size: 32px;
  /* font-weight: 600; */
}

.el-tabs--right .el-tabs__content,
.el-tabs--left .el-tabs__content {
  height: 100%;
}
</style>