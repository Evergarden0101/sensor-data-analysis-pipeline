<template>
    <NavBar/>
    <h1> This is the Emg Page!</h1>
    <DataSetSlider/>
    <!-- <DataSpace/> -->
</template>


<script>
import NavBar from '@/components/NavBar.vue';
import DataSetSlider from '../components/DataSetSlider.vue'
// import DataSpace from '../components/DataSpace.vue'
export default {
name: 'EmgPage',
components: {
    NavBar,
    DataSetSlider,
    // DataSpace,
},
};
</script>