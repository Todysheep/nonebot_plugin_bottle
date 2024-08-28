import request from '@/utils/request'

export function getUnapprovedBottles(params) {
  return request({
    url: 'api/getUnApprovedBottle',
    method: 'get',
    params: params
  })
}

export function approve(bottle_id) {
  return request({
    url: 'api/approve',
    method: 'post',
    data: {
      bottle_id: bottle_id
    }
  })
}

export function reject(bottle_id) {
  return request({
    url: 'api/reject',
    method: 'post',
    data: {
      bottle_id: bottle_id
    }
  })
}
