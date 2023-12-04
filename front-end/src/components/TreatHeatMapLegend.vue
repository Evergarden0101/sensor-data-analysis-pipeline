<template>
    <el-card>
        <template #header>
            <div class="card-header">
                <span><b>Legend</b></span>
            </div>
        </template>
        <p>
            <div class="box" style="margin-top: 3%; display: inline-block; margin-right: 4%; color:white; text-align: center; vertical-align: middle;">10</div> Events on specific week day and sleep cycle
        </p>
        <p>
            <div class="visualmap" style="margin-top: 3%; display: inline-block; margin-right: 4%; color:white; text-align: center; vertical-align: middle;" /># Events
        </p>
        </el-card> 
    </template>
    
    <script>
    export default {
        name: 'TreatHeatMapLegend',
    }
    </script>
    
    
    <style>
    .box {
        width:30px;
        height:25px;
        background-color: #A85555;
        position: relative; 
        line-height: 20px;
    }
    
    .visualmap {
        border-radius: 6px;
        background-image: linear-gradient(to left, #A85555, #FFE684);
        width: 45px;
        height: 15px;
    }
    </style>