<template>
    <h1 style="text-align: center; margin-bottom: 2%;"><el-icon :size="default"><Open /></el-icon> Events Classification</h1>
    <el-row style="margin-bottom: 1%;">
        <el-col align-center :span="16" :offset="4">
            <Stepper step=3 />
        </el-col>
    </el-row>

    <h2 align="center" style="margin-top: 2%;">Patient: {{ this.$store.state.patientId }}, Week: {{ this.$store.state.week }}, Night id: {{ this.$store.state.nightId }}</h2>
    <el-row style="margin-top: 2%;">
        <el-col :span="7" :offset="5">
            <router-link :to="'/filtering/'">
                <el-button type="primary" plain><el-icon class="el-icon--left"><ArrowLeft /></el-icon> Filtering</el-button>
            </router-link>
        </el-col>
        <el-col :span="7" :offset="5">
            <router-link :to="'/analysis/'">
                <el-button type="primary" plain :disabled="!monitoringAllowed">
                    Analysis<el-icon class="el-icon--right"><ArrowRight /></el-icon>
                </el-button>
            </router-link>
        </el-col>
    </el-row>
    <el-row style="margin-top: 2em;margin-bottom: 1em;height: 30px;overflow: visible; ">
        <el-col :span="3" :offset="20" style="margin-top: -150px;height: 130px;">
            <div class="affix-container">
                <el-affix target=".affix-container" :offset="10">
                    <p style="display: block;margin:0 auto 60px auto;text-align: center;">Weekly Summary</p>
                    <el-button @click="rerender" style="width: 200px;padding: 0;border: 0;">
                        <el-skeleton style="width: 200px" :loading="load_week_img" animated>
                            <template #template>
                                <el-skeleton-item variant="image" style="width: 200px;height:200px" />
                            </template>
                            <template #default>
                                <el-image :src="week_sum_imgsrc" :fit="contain" width="200px" @click="rerender"/>
                            </template>
                        </el-skeleton>
                    </el-button>
                    <el-dialog v-model="weekSummaryVisible" title="Weekly Summary" center width="60%">
                        <el-row>
                            <el-col :span="19">
                                <TreatHeatMap v-if="isShow"/>
                            </el-col>
                            <el-col :span="5">
                                <TreatHeatMapLegend />
                            </el-col>
                        </el-row>  
                    </el-dialog>
                </el-affix>
            </div>
        </el-col>
    </el-row>
    <el-row style="margin-bottom:3em;margin-top:-2%">
        <el-col :span="22" :offset="1">
            <!-- <el-card :body-style="{ padding: '5px' }" shadow="always" style="border-radius: 10px"> -->
                <h4 align="center">Signals and Predicted Events for Whole Night</h4>
                <el-skeleton style="width: 100%" :loading="load_night_img" animated>
                    <template #template>
                        <el-skeleton-item variant="image" style="width: 100%;height:40vh" />
                    </template>
                    <template #default>
                        <el-image :src="night_pred_imgsrc" :fit="fill"
                            :zoom-rate="1.2" :max-scale="7" :min-scale="0.2" :preview-src-list="[night_pred_imgsrc]"/>
                    </template>
                </el-skeleton>
                <!-- <el-image :src="night_pred_imgsrc" :fit="fill" v-loading="load_night_img"
                    :zoom-rate="1.2" :max-scale="7" :min-scale="0.2" :preview-src-list="[night_pred_imgsrc]"/> -->
            <!-- </el-card> -->
        </el-col>
    </el-row>
    <el-row>
        <el-col :span="11" style="padding-left: 1.5em;">
            <el-affix :offset="10">
                <BruxismLabel :key="this.$store.state.bruxLabelKey"></BruxismLabel>
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
import axios from 'axios';
import TreatHeatMapLegend from '@/components/TreatHeatMapLegend.vue';

export default {
    name: 'EventsClassificationPage',
    components: {
        Stepper,
        LinePlot,
        TreatHeatMap,
        BruxismLabel,
        TreatHeatMapLegend
    },
    data () {
        return {
            weekSummaryVisible: false,
            isShow: true,
            monitoringAllowed: false
            // imgsrc: require("@/assets/summary.png"),
            // week_sum_imgsrc: '',
            // night_pred_imgsrc: '',
         }
    },
    computed: {
        night_pred_imgsrc() {
            return this.$store.state.nightImg
        },
        week_sum_imgsrc() {
            return this.$store.state.weekImg
        },
        load_night_img() {
            return this.night_pred_imgsrc == ''
        },
        load_week_img() {
            return this.week_sum_imgsrc == ''
        }
    },
    async mounted(){
        await this.isMonitoringAllowed();
        // this.week_sum_imgsrc= "http://127.0.0.1:5000/weekly-sum-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week;
        // this.night_pred_imgsrc = "http://127.0.0.1:5000/night-pred-img?p=" + this.$store.state.patientId+'&w='+this.$store.state.week+'&n='+this.$store.state.nightId+'&r='+this.$store.state.recorder;
    },
    methods:{
        rerender(){
            this.weekSummaryVisible = true;
            this.isShow = false;
            this.$nextTick(() => {
                this.isShow = true;
            });
        },
        async isMonitoringAllowed(){
            const path = `http://127.0.0.1:5000/monitoring-allowed/${this.$store.state.patientId}/${this.$store.state.week}/`;
            const headers = { 
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            };
            await axios.get(path, {headers})
            .then((res) => {
                this.monitoringAllowed = res.data.is_allowed;
            })
            .catch(err=>{
                console.log(err)
            })
        }
    }
};
</script>
<style scoped>
.affix-container {
  text-align: right;
  height: 150px;
  border-radius: 4px;
  z-index: 9999;
  /* background: var(--el-color-primary-light-9); */
}
</style>
