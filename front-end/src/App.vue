<template>
  <el-row><HomeButton/></el-row>
  <div class="page-wrap">
    <router-view></router-view>
  </div>

</template>

<script>
import HomeButton from './components/HomeButton.vue';
export default {
  name: 'App',
  components: {
    HomeButton
  },
}
</script>
