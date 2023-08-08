<template>
  <el-form ref="form" :model="form" label-width="120px">
    <el-row class="demo-autocomplete">
      <p>Patient Name: </p>
      <el-autocomplete
        v-model="this.form.patientName"
        :fetch-suggestions="querySearch"
        clearable
        class="inline-input w-50"
        placeholder="Input Patient Name"
        @select="handleSelect"
        style="margin-left: 10px;margin-top: 8px;overflow: visible;"
      >
        <!-- <template #suffix>
          <el-icon class="el-input__icon" @click="handleIconClick">
            <edit />
          </el-icon>
        </template> -->
        <!-- <template #default="{ item }">
          <div class="value">{{ item.name }},&nbsp;&nbsp;id: {{ item.id }}</div>
        </template> -->
        <template #default="{ item }">
          <span style="float: left">{{ item.name }}</span>
          <span
            style="
              float: right;
              color: var(--el-text-color-secondary);
              font-size: 13px;
            "
            >id:&nbsp;&nbsp;{{ item.id }}</span>
        </template>
      </el-autocomplete>
    </el-row>
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

    <el-form-item v-if="form.filtered" label="Normalized">
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
          patientName: '',
          id:'',
          frequency: 1000,
          filtered: 0,
          normalized: 0,
        },
        names:[],
      };
    },
    methods: {
      onSubmit() {
        console.log(this.form.patientName);
        console.log(this.form.frequency);
        console.log(this.form.filtered);
        console.log(this.form.normalized);
      },
      handleChange(value) {
        console.log(value)
      },
      handleSelect(item) {
        console.log(item);
        this.form.patientName = item.name;
        this.form.id = item.id;
      },
      querySearch(queryString, cb) {
        var names = this.names;
        var results = queryString ? names.filter(this.createFilter(queryString)) : names;
        // call callback function to return suggestions
        cb(results);
      },
      createFilter(queryString) {
        return (id) => {
          return (id.name.toLowerCase().indexOf(queryString.toLowerCase()) === 0);
        };
      },
      loadAll() {
        return [
          { "name": "James", "id": "1" },
          { "name": "Luka", "id": "2" },
          { "name": "Davis", "id": "3" },
          { "name": "Jimmy", "id": "4" },
          { "name": "Stephen", "id": "5" },
          { "name": "Micheal", "id": "6" },
          { "name": "Tim", "id": "7" }
         ];
      },
    },
    beforeMount() {
      this.names = this.loadAll();
    }
}

</script>