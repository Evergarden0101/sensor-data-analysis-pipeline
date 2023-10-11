<template>
    <el-steps :active=step finish-status="process">
        <el-step title="Patient Information" description="Provide the patient information" />
        <el-step title="Filtering" description="Filter out undesired intervals" />
        <el-step title="Events Classification" description="Check for specific events in the data to label" />
        <el-step title="Events Monitoring" description="Compare patients data between different months, weeks and days" />
    </el-steps>
</template>


<script>
export default{
    name: "Stepper",
    props: ['step']
}
</script>
