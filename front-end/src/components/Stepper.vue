<template>
    <el-steps :active=step finish-status="process">
        <el-step title="Patient Information" description="Provide the patient information" />
        <!--<el-step title="Select patient" description="Select the desired patient and the desired day" />-->
        <el-step title="Sleep Stage Detection" description="Label sleep stages based on HRV analysis" />
        <el-step title="Events Classification Dashboard" description="Check for specific events in the data and label them" />
        <el-step title="Events Monitoring" description="Compare patients data in different days and weeks" />
    </el-steps>
</template>


<script>
export default{
    name: "Stepper",
    props: ['step']
}
</script>
