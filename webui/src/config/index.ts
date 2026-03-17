export const API_CONFIG = {
  BASE_URL: 'http://localhost:8010',
  VERSION: '/api/v1',
  get FULL_URL() {
    return `${this.BASE_URL}${this.VERSION}`
  }
}
