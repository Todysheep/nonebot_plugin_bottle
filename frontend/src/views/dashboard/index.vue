<template>
  <StatisticChart :statistic="statisticData" />
</template>

<script>
import StatisticChart from './statistic.vue'
import { getStatistic } from '@/api/dashboard'

export default {
  name: 'Dashboard',
  components: {
    StatisticChart
  },
  data() {
    return {
      statisticData: {
        total: 0,
        unapproved: 0,
        avl: 0,
        deleted: 0,
        days: [
          { date: '2024-08-20', count: 0 },
          { date: '2024-08-21', count: 0 },
          { date: '2024-08-22', count: 0 },
          { date: '2024-08-23', count: 0 },
          { date: '2024-08-24', count: 0 },
          { date: '2024-08-25', count: 0 },
          { date: '2024-08-26', count: 0 }
        ]
      }
    }
  },
  mounted() {
    this.getData()
  },
  methods: {
    getData() {
      getStatistic().then(data => {
        this.statisticData = data
      })
    }
  }
}
</script>
