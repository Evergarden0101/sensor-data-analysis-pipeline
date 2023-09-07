<template>
    <el-row style="margin-bottom: 2%;">
        <el-col>
            <h1 style="text-align: center;">This is the Settings page!</h1>
        </el-col>
    </el-row>

    <el-row justify="center">
        <SettingsForm />
    </el-row>
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