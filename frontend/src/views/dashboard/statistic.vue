<template>
  <div>
    <el-row>
      <el-col
        id="bar-chart"
        style="width: 50%; height: 400px"
        :span="12"
      />
      <el-col
        id="pie-chart"
        style="width: 50%; height: 400px"
        :span="12"
      />
    </el-row>
  </div>
</template>

<script>
import * as echarts from 'echarts'

export default {
  props: {
    statistic: {
      type: Object,
      required: true
    }
  },
  watch: {
    statistic: {
      handler() {
        this.renderBarChart()
        this.renderPieChart()
      },
      deep: true
    }
  },
  mounted() {
    this.renderBarChart()
    this.renderPieChart()
  },
  methods: {
    renderBarChart() {
      const barChart = echarts.init(document.getElementById('bar-chart'))
      const days = this.statistic.days.map((day) => day.date)
      const counts = this.statistic.days.map((day) => day.count)

      const option = {
        title: {
          text: '近7天'
        },
        xAxis: {
          type: 'category',
          data: days,
          axisLabel: {
            rotate: 45,
            interval: 0
          }
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            data: counts,
            type: 'bar'
          }
        ]
      }

      barChart.setOption(option)
    },
    renderPieChart() {
      const pieChart = echarts.init(document.getElementById('pie-chart'))

      const option = {
        title: {
          text: this.statistic.total.toString(),
          subtext: '总数',
          x: 'center',
          y: 'center',
          textStyle: {
            fontSize: 30
          }
        },
        tooltip: {
          trigger: 'item',
          formatter: '{b}: {c} ({d}%)'
        },
        legend: {
          orient: 'vertical',
          left: 'left',
          data: ['未审批', '有效', '已删除']
        },
        series: [
          {
            name: 'Statistics',
            type: 'pie',
            radius: ['50%', '70%'],
            avoidLabelOverlap: false,
            label: {
              show: true,
              position: 'outside',
              formatter: '{b}: {c}' // 标签显示部分名称和数量
            },
            emphasis: {
              label: {
                show: true,
                fontSize: '20',
                fontWeight: 'bold',
                formatter: '{b}: {c} ({d}%)' // 悬浮时显示详细信息
              }
            },
            labelLine: {
              show: true
            },
            data: [
              { value: this.statistic.unapproved, name: '未审批' },
              { value: this.statistic.avl, name: '有效' },
              { value: this.statistic.deleted, name: '已删除' }
            ]
          }
        ]
      }

      pieChart.setOption(option)

      // 添加点击事件监听器
      pieChart.on('click', (params) => {
        if (params.name === '未审批') {
          this.$router.push({ path: '/approve/approve' })
        } else if (params.name === '有效') {
          this.$router.push({ path: '/bottles/bottles' })
        }
      })
    }
  }
}
</script>

<style scoped>
#bar-chart,
#pie-chart {
  margin: 0 auto;
}
</style>
