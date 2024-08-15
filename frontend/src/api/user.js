import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/api/token',
    method: 'post',
    data
  })
}

export function refreshToken(data) {
  return request({
    url: '/api/refresh',
    method: 'post',
    data
  })
}
