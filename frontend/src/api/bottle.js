import request from '@/utils/request'

export function getBottles(params) {
  return request({
    url: 'api/getBottles',
    method: 'get',
    params: params
  })
}
