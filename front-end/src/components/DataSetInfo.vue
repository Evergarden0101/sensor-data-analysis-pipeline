<template>
  <el-form ref="form" :model="form" label-width="120px">
    <el-form-item label="Patient UID">
      <el-autocomplete
        v-model="this.form.patientId"
        :fetch-suggestions="querySearch"
        clearable
        class="inline-input w-50"
        placeholder="Input Patient UID"
        @select="handleSelect"
        style="overflow: visible;"
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
    <el-form-item label="Frequency">
        <el-input-number v-model="form.frequency" @change="handleChange" :min="20" :max="2000"></el-input-number>
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
          patientId: '',
          id:'',
          frequency: 1000,
          filtered: 0,
          normalized: 0,
        },
        ids:[],
      };
    },
    methods: {
      onSubmit() {
        console.log(this.form.patientId);
        console.log(this.form.frequency);
        console.log(this.form.filtered);
        console.log(this.form.normalized);
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
}

</script>