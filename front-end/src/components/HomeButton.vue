<template>
    <router-link :to="'/'">

        <el-button type="primary">
            <el-icon size=18><HomeFilled /></el-icon>
             Home
        </el-button>
    </router-link>
</template>

<script>
export default{
    name: 'HomeButton',
}
</script>