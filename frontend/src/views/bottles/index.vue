<template>
  <div>
    <el-row :gutter="20">
      <el-col v-for="bottle in bottles" :key="bottle.id" :span="6">
        <el-card shadow="hover">
          <template #header>
            <span>{{ bottle.id }} ({{ bottle.group_name }})</span>
          </template>
          <div>{{ bottle.content }}</div>
          <el-divider />
          <div v-for="comment in bottle.comment.slice(0, 3)" :key="comment.time">
            <p>
              <strong>{{ comment.user_name }}:</strong> {{ comment.content }}
            </p>
            <p style="font-size: 12px; color: gray;">{{ comment.time }}</p>
          </div>
          <el-divider />
          <div>
            <el-tag>
              👍 {{ bottle.like }}
            </el-tag>
            <el-tag type="warning">捡: {{ bottle.picked }}</el-tag>
            <el-tag type="danger">举报: {{ bottle.report }}</el-tag>
          </div>
          <el-button type="primary" icon="el-icon-search" style="margin-top: 10px; float: right;"
            @click="showDetails(bottle)">
          </el-button>
        </el-card>
      </el-col>
    </el-row>

    <div style="margin-top: 20px; text-align: center;">
      <el-pagination background layout="prev, pager, next" :total="total" :page-size="pageSize"
        @current-change="handlePageChange" />
    </div>

    <el-dialog :visible.sync="dialogVisible" width="50%" :title="selectedBottle ? 'Bottle ' + selectedBottle.id : ''">
      <div v-if="selectedBottle">
        <p><strong>群:</strong> {{ selectedBottle.group_name }}</p>
        <p><strong>内容:</strong> {{ selectedBottle.content }}</p>
        <el-divider />
        <div v-for="comment in selectedBottle.comment" :key="comment.time">
          <p>
            <strong>{{ comment.user_name }}:</strong> {{ comment.content }}
          </p>
          <p style="font-size: 12px; color: gray;">{{ comment.time }}</p>
        </div>
        <el-divider />
        <div>
          <el-tag>
            👍 {{ selectedBottle.like }}
          </el-tag>
          <el-tag type="warning">捡: {{ selectedBottle.picked }}</el-tag>
          <el-tag type="danger">举报: {{ selectedBottle.report }}</el-tag>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script>
import { getBottles } from '@/api/bottle'

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
    showDetails(bottle) {
      this.selectedBottle = bottle
      this.dialogVisible = true
    }
  }
}
</script>
