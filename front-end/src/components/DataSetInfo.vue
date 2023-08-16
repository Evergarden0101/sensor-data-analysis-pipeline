<template>
  <el-form ref="form" :model="form" label-width="120px" style="display: block;margin: auto;">
    <el-form-item label="Week">
        <el-input-number v-model="form.week" placeholder="Input week number" :controls="false"/>
    </el-form-item>
    <el-form-item label="Day">
        <el-select v-model="form.day" placeholder="Select record day" style="width: 155px">
                <el-option
                        v-for="item in days"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    />
        </el-select>
    </el-form-item>
    <el-form-item label="Frequency">
        <el-input-number v-model="form.frequency" :min="20" :max="2000"></el-input-number>
        <el-text size="large" style="margin-left: 0.3em;">Hz</el-text>
    </el-form-item>

    <el-form-item label="Filtered">
        <el-switch
            v-model="form.filtered"
            active-text="Yes"
            inactive-text="No">
        </el-switch>
    </el-form-item>

    <el-form-item v-if="form.filtered" label="Normalized">
        <el-switch
            v-model="form.normalized"
            active-text="Yes"
            inactive-text="No">
        </el-switch>
    </el-form-item>

    <!-- <el-form-item>
        <router-link :to="'/sleep/'" style="margin-right: 20px;">
            <el-button type="primary" plain @click="onSubmit">Create</el-button>  
        </router-link>
    </el-form-item> -->
  </el-form>
</template>

<script>
export default{
    name: "DataSetInfo",
    data() {
      return {
        form: {
          frequency: 1000,
          filtered: 0,
          normalized: 0,
          week:null,
          day:'',
        },
        days : [
            {
                value: 'Day1',
                label: 'Day 1',
            },
            {
                value: 'Day2',
                label: 'Day 2',
            },
            {
                value: 'Day3',
                label: 'Day 3'
            },
            {
                value: 'Day4',
                label: 'Day 4'
            },
            {
                value: 'Day5',
                label: 'Day 5'
            },
            {
                value: 'Day6',
                label: 'Day 6'
            },
            {
                value: 'Day7',
                label: 'Day 7'
            },
        ]
      };
    },
    methods: {
      onSubmit() {
        console.log(this.form.patientId);
        console.log(this.form.frequency);
        console.log(this.form.filtered);
        console.log(this.form.normalized);
      },
      
    },
}

</script>