<template>
  <div>
    <el-row :gutter="20">
      <el-col v-for="bottle in bottles" :key="bottle.id" :span="6">
        <el-card class="bottle-card" shadow="hover" @click.native="showDetails(bottle)">
          <template #header>
            <div class="header-container">
              <span class="bottle-id">{{ bottle.id }}</span>
              <span class="group-name">{{ bottle.group_name }}({{ bottle.group_id }})<br><i class="el-icon-user" />{{ bottle.user_name }}({{ bottle.user_id }})</span>
            </div>
          </template>
          <div v-html="sanitizedContent(bottle.content)" />
          <el-divider />
          <div v-for="comment in bottle.comment.slice(0, 3)" :key="comment.id">
            <p>
              <strong>{{ comment.user_name }}:</strong> {{ comment.content }}
            </p>
            <p style="font-size: 12px; color: gray">{{ comment.time }}</p>
          </div>
          <el-divider />
          <div class="bottle-info-icon-container">
            <el-tag> 👍 {{ bottle.like }} </el-tag>
            <el-tag type="warning"> 🤚 {{ bottle.picked }}</el-tag>
            <el-tag type="danger"> 🚩 {{ bottle.report }}</el-tag>
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
      :title="selectedBottle ? 'Bottle ' + selectedBottle.id : ''"
      custom-class="bottle-dialog"
    >
      <div v-if="selectedBottle">
        <p><strong>群:</strong> {{ selectedBottle.group_name }}</p>
        <div v-html="sanitizedContent(selectedBottle.content)" />
        <el-divider />
        <div v-for="comment in selectedBottle.comment" :key="comment.id">
          <p>
            <strong>{{ comment.user_name }}:</strong> {{ comment.content }}
          </p>
          <p style="font-size: 12px; color: gray">{{ comment.time }}</p>
        </div>
        <el-divider />
        <div class="bottle-info-icon-container">
          <el-tag> 👍 {{ selectedBottle.like }} </el-tag>
          <el-tag type="warning"> 🤚 {{ selectedBottle.picked }}</el-tag>
          <el-tag type="danger"> 🚩 {{ selectedBottle.report }}</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getBottles, getComments } from '@/api/bottle'
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
        const response = await getBottles({
          page: this.currentPage - 1,
          page_size: this.pageSize
        })
        this.bottles = response
      } catch (error) {
        console.error('Error fetching bottles:', error)
      }
    },
    handlePageChange(page) {
      this.currentPage = page
      this.fetchBottles()
    },
    async showDetails(bottle) {
      this.selectedBottle = bottle
      this.dialogVisible = true

      try {
        const comments = await getComments({ bottle_id: bottle.id })
        this.selectedBottle.comment = comments
      } catch (error) {
        console.error('Error fetching comments:', error)
      }
    }
  }
}
</script>

<style lang="scss" scoped>
.bottle-card {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  border-radius: 20px;
  border-top: 4px solid #409EFF;
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
  font-size: 30px; /* Adjust size as needed */
  color: #409EFF; /* Blue color */
  font-weight: bold; /* Optional: make text bold */
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
