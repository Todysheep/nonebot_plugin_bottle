import request from '@/utils/request'

export function getBottles(params) {
  return request({
    url: 'api/getBottles',
    method: 'get',
    params: params
  })
}

export function getComments(params) {
  return request({
    url: 'api/getComments',
    method: 'get',
    params: params
  })
}
