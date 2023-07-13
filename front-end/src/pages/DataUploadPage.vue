<template>
    <h2>This is the Data Upload Page</h2>

    <!-- <div class="hp-icons-container"> -->
        <el-row style="margin-top: 50px;">
            <DataSetSlider/>
        </el-row>

        <el-row style="margin-top: 50px;">
            <router-link :to="'/sleep/'" style="margin-right: 20px;">
                <button>Sleep Stage Classification</button>  
            </router-link>

            <router-link :to="'/bruxism/'" style="margin-right: 20px;">
                <button>Bruxism Detection</button>  
            </router-link>
            
            <router-link :to="'/treatment/'" style="margin-right: 20px;">
                <button>Treatment Analysis</button> 
            </router-link>

        </el-row>
        
    <!-- </div> -->
</template>

<script>
import DataSetSlider from '../components/DataSetSlider.vue'
export default {
    name: 'DataUploadPage',
    components: {
        DataSetSlider,
    },
};
</script>
  