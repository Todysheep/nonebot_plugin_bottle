<template>
  <div>
    <el-row :gutter="20" style="margin: 20px">
      <el-col v-for="bottle in bottles" :key="bottle.id" :span="6">
        <el-card
          class="bottle-card"
          shadow="hover"
          @click.native="showDetails(bottle)"
        >
          <template #header>
            <div class="header-container">
              <span class="bottle-id">{{ bottle.id }}</span>
              <span
                class="group-name"
              >{{ bottle.group_name }}({{ bottle.group_id }})<br><i class="el-icon-user" />{{ bottle.user_name }}({{ bottle.user_id }})</span>
            </div>
          </template>
          <div v-html="sanitizedContent(bottle.content)" />
          <div class="bottle-info-icon-container">
            <el-tag> 👍 {{ bottle.like }} </el-tag>
            <el-tag type="warning"> 🤚 {{ bottle.picked }}</el-tag>
            <el-tag type="danger"> 🚩 {{ bottle.report }}</el-tag>
          </div>
          <div style="text-align: center; margin-top: 10px">
            <el-button type="success" @click.stop="approveBottle(bottle.id)">
              通过
            </el-button>
            <el-button type="danger" @click.stop="rejectBottle(bottle.id)">
              拒绝
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top: 20px; text-align: center">
      <el-pagination
        background
        layout="prev, pager, next"
        :total="total"
        :page-size="pageSize"
        @current-change="handlePageChange"
      />
    </div>

    <el-dialog
      :visible.sync="dialogVisible"
      width="50%"
      :title="selectedBottle ? '漂流瓶 ' + selectedBottle.id : ''"
      custom-class="bottle-dialog"
    >
      <div v-if="selectedBottle">
        <p>
          <strong>群:</strong> {{ selectedBottle.group_name }}({{
            selectedBottle.group_id
          }})
        </p>
        <p>
          <strong>用户:</strong> {{ selectedBottle.user_name }}({{
            selectedBottle.user_id
          }})
        </p>
        <div v-html="sanitizedContent(selectedBottle.content)" />
        <div class="bottle-info-icon-container">
          <el-tag> 👍 {{ selectedBottle.like }} </el-tag>
          <el-tag type="warning"> 🤚 {{ selectedBottle.picked }}</el-tag>
          <el-tag type="danger"> 🚩 {{ selectedBottle.report }}</el-tag>
        </div>
      </div>
      <div style="text-align: center; margin-top: 20px">
        <el-button type="success" @click="approveBottle(selectedBottle.id)">
          通过
        </el-button>
        <el-button type="danger" @click="rejectBottle(selectedBottle.id)">
          拒绝
        </el-button>
        <el-button @click="showNextBottle">下一条</el-button>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getUnapprovedBottles, approve, reject } from '@/api/approve'
import DOMPurify from 'dompurify'

export default {
  data() {
    return {
      bottles: [],
      total: 0,
      pageSize: 10,
      currentPage: 1,
      dialogVisible: false,
      selectedBottle: null
    }
  },
  mounted() {
    this.fetchBottles()
  },
  methods: {
    sanitizedContent(content) {
      return DOMPurify.sanitize(content)
    },
    async fetchBottles() {
      try {
        const response = await getUnapprovedBottles({
          page: this.currentPage - 1,
          page_size: this.pageSize
        })
        this.bottles = response.bottles
        this.total = response.total
      } catch (error) {
        console.error('Error fetching bottles:', error)
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchBottles()
    },
    showDetails(bottle) {
      this.selectedBottle = bottle
      this.dialogVisible = true
    },
    async approveBottle(bottle_id) {
      try {
        const response = await approve(bottle_id)
        if (response.code === 0) {
          this.$message.success(response.msg)
          this.removeBottle(bottle_id)
          this.showNextBottle()
        } else {
          this.$message.error(response.msg)
        }
      } catch (error) {
        console.error('Error approving bottle:', error)
        this.$message.error('操作失败')
      }
    },
    async rejectBottle(bottle_id) {
      try {
        const response = await reject(bottle_id)
        if (response.code === 0) {
          this.$message.success(response.msg)
          this.removeBottle(bottle_id)
          this.showNextBottle()
        } else {
          this.$message.error(response.msg)
        }
      } catch (error) {
        console.error('Error rejecting bottle:', error)
        this.$message.error('操作失败')
      }
    },
    removeBottle(bottle_id) {
      this.bottles = this.bottles.filter(bottle => bottle.id !== bottle_id)
    },
    showNextBottle() {
      if (this.dialogVisible === false) {
        return
      }
      const currentIndex = this.bottles.findIndex(
        bottle => bottle.id === this.selectedBottle.id
      )
      const nextBottle =
        this.bottles[currentIndex + 1] || this.bottles[0] || null
      if (nextBottle) {
        this.showDetails(nextBottle)
      } else {
        this.dialogVisible = false
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.bottle-card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  border-top: 4px solid #409eff;
  margin-bottom: 20px;
  transition: box-shadow 0.3s ease;
}

.bottle-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  cursor: pointer;
}

.bottle-info-icon-container {
  display: flex;
  justify-content: center;
  width: 100%;
  gap: 20px;
}

.bottle-dialog .el-dialog__header {
  border-radius: 20px 20px 0 0;
}

.bottle-dialog .el-dialog__body {
  border-radius: 0 0 20px 20px;
}

.bottle-dialog .el-dialog__wrapper {
  background-color: rgba(0, 0, 0, 0.5);
}

.header-container {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-container .group-name {
  position: absolute;
  bottom: 0px;
  right: 10px;
  font-size: 12px;
  color: gray;
  text-align: center;
}

.header-container .bottle-id {
  font-size: 30px;
  color: #409eff;
  font-weight: bold;
}
</style>

<style>
.bottle-content {
  max-width: 600px;
  margin: 0 auto;
}

.bottle-cached-image {
  width: 100%;
  max-width: 100%;
  height: auto;
  object-fit: contain;
}
</style>
