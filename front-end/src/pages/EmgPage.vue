<template>
    <NavBar/>
    <h1> This is the Emg Page!</h1>
    <DataSetSlider/>
    <!-- <DataSpace/> -->
    <LinePlot/>
</template>


<script>
import NavBar from '@/components/NavBar.vue';
import DataSetSlider from '../components/DataSetSlider.vue'
import DataSpace from '../components/DataSpace.vue'
import LinePlot from '../components/LinePlot.vue'
export default {
name: 'EmgPage',
components: {
    NavBar,
    DataSetSlider,
    DataSpace,
    LinePlot,
},
};
</script>