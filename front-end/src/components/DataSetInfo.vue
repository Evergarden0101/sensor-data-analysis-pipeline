<template>
  <el-form ref="form" :model="form" label-width="120px">
    <el-form-item label="Frequency">
        <el-input-number v-model="form.frequency" @change="handleChange" :min="20" :max="2000"></el-input-number>
    </el-form-item>

    <el-form-item label="Filtered">
        <el-switch
            v-model="form.filtered"
            active-text="Yes"
            inactive-text="No">
        </el-switch>
    </el-form-item>

    <el-form-item v-if="form.filtered">
        <el-switch
            v-model="form.normalized"
            active-text="Yes"
            inactive-text="No">
        </el-switch>
    </el-form-item>


    <el-form-item>
        <router-link :to="'/sleep/'" style="margin-right: 20px;">
            <el-button type="primary" @click="onSubmit">Create</el-button>  
        </router-link>
    </el-form-item>

    



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

        },
      };
    },
    methods: {
      onSubmit() {
        console.log(this.form.frequency);
        console.log(this.form.filtered);
        console.log(this.form.normalized);
      },
      handleChange(value) {
        console.log(value)
      },

    }
}

</script>