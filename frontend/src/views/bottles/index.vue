<template>
  <div>
    <div style="margin: 20px">
      <el-row :gutter="20" type="flex" justify="center">
        <el-col :span="6">
          <el-input
            v-model="searchParams.bottle_id"
            placeholder="漂流瓶ID"
            clearable
            style="width: 100%"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchParams.group_id"
            placeholder="群号"
            clearable
            style="width: 100%"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchParams.user_id"
            placeholder="用户号"
            clearable
            style="width: 100%"
          />
        </el-col>
        <el-col :span="6">
          <el-input
            v-model="searchParams.content"
            placeholder="内容（模糊）"
            clearable
            style="width: 100%"
          />
        </el-col>
      </el-row>
      <div style="text-align: center; margin-top: 10px">
        <el-button type="primary" @click="resetSearch">重置</el-button>
        <el-button type="primary" @click="searchBottles">查询</el-button>
      </div>
    </div>
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
          <div class="content-preview">
            <div class="content-container" v-html="sanitizedContent(bottle.content)" />
          </div>
          <el-divider />
          <div class="bottom-section">
            <!-- <div v-for="comment in bottle.comment.slice(0, 3)" :key="comment.id">
              <p>
                <strong>{{ comment.user_name }}:</strong> {{ comment.content }}
              </p>
              <p style="font-size: 12px; color: gray">{{ comment.time }}</p>
            </div>
            <el-divider /> -->
            <div class="bottle-info-icon-container">
              <el-tag> 👍 {{ bottle.like }} </el-tag>
              <el-tag type="warning"> 🤚 {{ bottle.picked }}</el-tag>
              <el-tag type="danger"> 🚩 {{ bottle.report }}</el-tag>
            </div>
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
      selectedBottle: null,
      searchParams: {
        bottle_id: '',
        group_id: '',
        user_id: '',
        content: ''
      }
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
          page_size: this.pageSize,
          ...this.searchParams
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
    async showDetails(bottle) {
      this.selectedBottle = bottle
      this.dialogVisible = true

      try {
        const comments = await getComments({ bottle_id: bottle.id })
        this.selectedBottle.comment = comments
      } catch (error) {
        console.error('Error fetching comments:', error)
      }
    },
    searchBottles() {
      this.currentPage = 1
      this.fetchBottles()
    },
    resetSearch() {
      this.currentPage = 1
      this.searchParams.bottle_id = ''
      this.searchParams.group_id = ''
      this.searchParams.user_id = ''
      this.searchParams.content = ''
      this.fetchBottles()
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
  display: flex;
  flex-direction: column;
  height: 40vh;
}

.bottle-card:hover {
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.5);
  cursor: pointer;
}

.content-preview {
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
}

.content-container {
  height: 18vh;
  overflow: hidden;
}

.bottle-info-icon-container {
  display: flex;
  justify-content: center;
  width: 100%;
  gap: 20px;
  margin-top: auto;
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

.bottle-dialog .el-dialog__header {
  border-radius: 20px 20px 0 0;
}

.bottle-dialog .el-dialog__body {
  border-radius: 0 0 20px 20px;
}

.bottle-dialog .el-dialog__wrapper {
  background-color: rgba(0, 0, 0, 0.5);
}

.bottom-section {
  margin-top: auto;
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
