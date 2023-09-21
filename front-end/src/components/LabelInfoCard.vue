<template>
    <el-popover 
        :width="500" placement="top-start"
        popper-style="box-shadow: rgb(14 18 22 / 35%) 0px 10px 38px -10px, rgb(14 18 22 / 20%) 0px 10px 20px -15px; padding: 20px;"
        >
        <template #reference>
            <el-icon><InfoFilled /></el-icon>
        </template>
        <template #default>
            <!-- <div
            class="demo-rich-conent"
            style="display: flex; gap: 16px; flex-direction: column"
            > -->
            <el-row>
                <el-col :span="11">
                    <el-statistic :value="peakMR" precision="3">
                        <template #title>
                            <div style="display: inline-flex; align-items: center;font-weight: bold;font-size: 15px;">
                                Peak MR Signal
                            </div>
                        </template>
                    </el-statistic>
                    <div class="statistic-footer">
                        <div class="footer-item">
                            <span>than recorded</span>
                            <span class="green">
                            33%
                            <el-icon>
                                <CaretTop />
                            </el-icon>
                            </span>
                        </div>
                    </div>
                </el-col>

                <el-col :span="11" :offset="2">
                    <el-statistic :value="peakML" precision="3">
                        <template #title>
                            <div style="display: inline-flex; align-items: center;font-weight: bold;font-size: 15px;">
                                Peak ML Signal
                            </div>
                        </template>
                    </el-statistic>
                    <div class="statistic-footer">
                        <div class="footer-item">
                            <span>than recorded</span>
                            <span class="green">
                            54%
                            <el-icon>
                                <CaretTop />
                            </el-icon>
                            </span>
                        </div>
                    </div>
                </el-col>
            </el-row>
            <el-row style="margin-top: 15px;">
                <el-col :span="11">
                    <el-statistic :value="avgMR" precision="3">
                        <template #title>
                            <div style="display: inline-flex; align-items: center;font-weight: bold;font-size: 15px;">
                                Average MR Signal
                            </div>
                        </template>
                    </el-statistic>
                    <div class="statistic-footer">
                        <div class="footer-item">
                            <span>than recorded</span>
                            <span class="red">
                            19%
                            <el-icon>
                                <CaretBottom />
                            </el-icon>
                            </span>
                        </div>
                    </div>
                </el-col>

                <el-col :span="11" :offset="2">
                    <el-statistic :value="avgML" precision="3">
                        <template #title>
                            <div style="display: inline-flex; align-items: center;font-weight: bold;font-size: 15px;">
                                Average ML Signal
                            </div>
                        </template>
                    </el-statistic>
                    <div class="statistic-footer">
                        <div class="footer-item">
                            <span>than recorded</span>
                            <span class="green">
                            23%
                            <el-icon>
                                <CaretTop />
                            </el-icon>
                            </span>
                        </div>
                    </div>
                </el-col>
            </el-row>
        </template>
    </el-popover>
</template>

<script setup>
import {
  ArrowRight,
  CaretBottom,
  CaretTop,
  Warning,
} from '@element-plus/icons-vue'
</script>

<script>
export default {
    name: 'LabelInfoCard',
    components: {
    },
    data () {
        return{
            peakMR: 3.124,
            peakML: 5.053,
            avgMR: 1.233,
            avgML: 1.722,
        }
    },
}
</script>

<style scoped>
:global(h2#card-usage ~ .example .example-showcase) {
  background-color: var(--el-fill-color) !important;
}

.el-statistic {
  --el-statistic-content-font-size: 28px;
}

.statistic-card {
  height: 100%;
  padding: 20px;
  border-radius: 4px;
  background-color: var(--el-bg-color-overlay);
}

.statistic-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  font-size: 10px;
  color: var(--el-text-color-regular);
  margin-top: 5px;
}

.statistic-footer .footer-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.statistic-footer .footer-item span:last-child {
  display: inline-flex;
  align-items: center;
  margin-left: 4px;
}

.green {
  color: var(--el-color-success);
}
.red {
  color: var(--el-color-error);
}
</style>