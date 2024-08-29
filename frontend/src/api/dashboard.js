import request from '@/utils/request'

export function getStatistic() {
  return request({
    url: 'api/statistic',
    method: 'get'
  })
}
