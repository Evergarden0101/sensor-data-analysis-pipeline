<template>
    <el-steps :active=step finish-status="process">
        <el-step title="Patient Information" description="Select the desired patient" />
        <el-step title="Filtering" description="Filter out undesired intervals" />
        <el-step title="Events Classification" description="Label events in the data" />
        <el-step title="Treatment Analysis" description="Compare data between different days and weeks" />
    </el-steps>
</template>


<script>
export default{
    name: "Stepper",
    props: ['step']
}
</script>
