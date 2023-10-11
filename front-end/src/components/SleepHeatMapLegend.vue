<template>
<el-card>
    <template #header>
        <div class="card-header">
            <span><b>Legend</b></span>
            <p>Every row represents a sleep cycle of 90 minutes (1.5 hour)</p>
            <p>Median and interquartile SD of REM phases from Herzig study: 105.5 (82.6, 134.7)  </p>

        </div>
    </template>
    <p>
        <div class="rem-box" style="margin-top: 3%; display: inline-block; margin-right: 4%; color:white; text-align: center; vertical-align: middle;">REM</div>REM interval (5 min)
    </p>
    <p>
        <div class="nrem-box" style="margin-top: 3%; display: inline-block; margin-right: 4%; vertical-align: middle;" />NREM interval (5 min)
    </p>
    <p>
        <div class="rem-visualmap" style="margin-top: 3%; display: inline-block; margin-right: 4%; color:white; text-align: center; vertical-align: middle;" />REM intervals uncertainity (SD) <el-tooltip placement="top" effect="light">
    <template #content>The level of uncertainity is derived from the Standard deviation of the LF/HF measure of the Heart Rate Variability (HRV) analyis. <br /> The ranges to classify the different sleep stages were taken from the following study: <br /><a href="https://www.frontiersin.org/articles/10.3389/fphys.2017.01100/full">Herzig, David, et al. "Reproducibility of heart rate variability is parameter and sleep stage dependent." Frontiers in physiology 8 (2018): 1100.</a> </template>
        <el-button size="small" circle ><el-icon><InfoFilled /></el-icon></el-button>
    </el-tooltip>
        </p>
        <p>
            <div class="nrem-visualmap" style="margin-top: 3%; display: inline-block; margin-right: 4%; color:white; text-align: center; vertical-align: middle;" />NREM intervals uncertainity (SD) <el-tooltip placement="top" effect="light">
    <template #content>The level of uncertainity is derived from the Standard deviation of the LF/HF measure of the Heart Rate Variability (HRV) analyis. <br /> The ranges to classify the different sleep stages were taken from the following study: <br /><a href="https://www.frontiersin.org/articles/10.3389/fphys.2017.01100/full">Herzig, David, et al. "Reproducibility of heart rate variability is parameter and sleep stage dependent." Frontiers in physiology 8 (2018): 1100.</a> </template>
    <el-button size="small" circle ><el-icon><InfoFilled /></el-icon></el-button>
    </el-tooltip>
        </p>
        <p>
            <div class="dashed-box" style="margin-top: 3%; display: inline-block; margin-right: 4%; vertical-align: middle; text-align: center;" >*</div>Selected intervals in default mode
        </p>
        <p><div class="box" style="margin-top: 3%; display: inline-block; margin-right: 4%; vertical-align: middle;"/>Selected intervals in edit mode</p>
    </el-card> 
    </template>
<script>
export default {
    name: 'SleepHeatMapLegend'
}
</script>


<style>
.dashed-box {
    width:50px;
    height:40px;
    border-style:dashed; border-width:3px;
    position: relative; 
    line-height: 40px
}
.box {
    width:50px;
    height:40px;
    border-style: solid; border-width:3px;
    position: relative; 
}

.rem-box {
    width:50px;
    height:40px;
    background-color: #1919ff;
    position: relative; 
    line-height: 40px;
}

.nrem-box {
    width:50px;
    height:40px;
    background-color: grey;
    position: relative;
}

.rem-visualmap {
    border-radius: 6px;
    background-image: linear-gradient(to right, #1919ff, #CCCCFF);
    width: 60px;
    height: 20px;
}

.nrem-visualmap {
    border-radius: 6px;
    background-image: linear-gradient(to right, #999999, #eeeeee);
    width: 60px;
    height: 20px;
}
</style>