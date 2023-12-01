<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;"> <el-icon :size="default"><Setting /></el-icon> Settings</h1>
        </el-col>
    </el-row>

    <div style="margin: 0px;">
        <div style="position: relative;
            width: 100%;
            display:flex;
            justify-content: center;
            align-items: center;
            text-align: center;"
        >
            <el-card style="width:600px; margin:auto;text-align:center">
                <SettingsForm />
            </el-card>
        </div>
    </div>
    
        
</template>

<script>
import SettingsForm from '@/components/SettingsForm.vue';

export default {
    name: 'SettingsPage',
    components: {
        SettingsForm
    }

};
</script>