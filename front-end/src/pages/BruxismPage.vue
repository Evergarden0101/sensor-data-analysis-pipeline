<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the Events Detection page!</h1>
        </el-col>
    </el-row>
    <el-row>
        <el-col align-center :span="12" :offset="6">
            <Stepper step=3 />
        </el-col>
    </el-row>
    <h2 align="center">Patient: {{ this.$store.state.patientId }}, Week: {{ this.$store.state.week }}, Night id: {{ this.$store.state.nightId }}</h2>
    <el-row style="margin-top: 3%;">
        <el-col :span="7" :offset="5">
            <router-link :to="'/sleep/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Sleep Stage Detection</el-button>
            </router-link>
        </el-col>
        <el-col :span="7" :offset="5">
            <router-link :to="'/treatment/'">
                <el-button type="primary" plain>
                    Treatment Analysis<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
            </router-link>
        </el-col>
    </el-row>
    <el-row style="margin-top: 2em;margin-bottom: 2em;height: 30px;overflow: visible; ">
        <el-col :span="3" :offset="20" style="margin-top: -150px;height: 130px;">
            <div class="affix-container">
                <el-affix target=".affix-container" :offset="10">
                    <p style="display: block;margin:0 auto 50px auto;text-align: center;">Weekly Summary</p>
                    <el-button @click="rerender" style="width: 200px;padding: 0;border: 0;">
                        <el-image :src="imgsrc" :fit="contain" width="200px" @click="rerender"/>
                    </el-button>
                    <el-dialog v-model="weekSummaryVisible" title="Weekly Summary" center width="60%">
                        <TreatHeatMap v-if="isShow"/>
                    </el-dialog>
                </el-affix>
            </div>
        </el-col>
    </el-row>

    <el-row>
        <el-col :span="11" style="padding-left: 1.5em;">
            <el-affix :offset="10">
                <BruxismLabel/>
            </el-affix>
        </el-col>
        <el-col :span="11" :offset="1">
            <LinePlot :key="this.$store.state.linePlotKey"></LinePlot>
        </el-col>
    </el-row>
</template>


<script>
import Stepper from '@/components/Stepper.vue';
// import DataSpace from '../components/DataSpace.vue'
import LinePlot from '../components/LinePlot.vue'
import TreatHeatMap from '../components/TreatHeatMap.vue'
// import { Orange } from '@element-plus/icons-vue'
import BruxismLabel from '@/components/BruxismLabel.vue';

export default {
    name: 'BruxismPage',
    components: {
        Stepper,
        LinePlot,
        TreatHeatMap,
        BruxismLabel
    },
    data () {
        return {
            weekSummaryVisible: false,
            isShow: true,
            // imgsrc: require("@/assets/summary.png"),
            imgsrc: '',
         }
    },
    mounted(){
        this.imgsrc= "http://127.0.0.1:5000/weekly-sum-img?skuid=p" + this.$store.state.patientId+'_w'+this.$store.state.week;
    },
    methods:{
        rerender(){
            this.weekSummaryVisible = true;
            this.isShow = false;
            this.$nextTick(() => {
                this.isShow = true;
            });
        }
    }
};
</script>
<style scoped>
.affix-container {
  text-align: right;
  height: 300px;
  border-radius: 4px;
  z-index: 9999;
  /* background: var(--el-color-primary-light-9); */
}
</style>