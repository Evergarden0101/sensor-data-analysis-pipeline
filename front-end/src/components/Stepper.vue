<template>
    <el-steps :active="step">
        <el-step title="Data upload" description="Some description" />
        <el-step title="Sleep Stage Classification" description="Some description" />
        <el-step title="Brux Classification Dashboard" description="Some description" />
        <el-step title="Brux Events Monitoring" description="Some description" />
    </el-steps>
</template>


<script>
export default{
    name: "Stepper",
    props: ['step']
}
</script>