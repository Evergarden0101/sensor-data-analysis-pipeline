<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the Settings page!</h1>
        </el-col>
    </el-row>

    <div style="display: flex; justify-content: center;">
        <el-card>
            <SettingsForm />
        </el-card>
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