export function formatDate(timestamp: number | string, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!timestamp) return ''
  
  const date = new Date(typeof timestamp === 'string' ? parseInt(timestamp) : timestamp)
  if (isNaN(date.getTime())) return ''
  
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  
  return format
    .replace('YYYY', String(year))
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
    .replace('ss', seconds)
}

export function formatTimestamp(timestamp: number | string | undefined | null, format: string = 'YYYY-MM-DD HH:mm:ss'): string {
  if (!timestamp) return '-'
  
  const ts = typeof timestamp === 'string' ? parseInt(timestamp) : timestamp
  if (isNaN(ts) || ts === 0) return '-'
  
  return formatDate(ts * 1000, format)
}

export function formatNumber(value: number | string, decimals: number = 2): string {
  if (value === null || value === undefined || value === '') return '0'
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '0'
  return num.toFixed(decimals)
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${(bytes / Math.pow(k, i)).toFixed(2)} ${sizes[i]}`
}

export function formatWeight(weight: number | undefined): string {
  if (weight === null || weight === undefined) return '-'
  return `${formatNumber(weight)} kg`
}

export function formatVolume(volume: number | undefined): string {
  if (volume === null || volume === undefined) return '-'
  return `${formatNumber(volume, 3)} m³`
}

export function formatCurrency(amount: number | string): string {
  if (amount === null || amount === undefined || amount === '') return '¥0.00'
  const num = typeof amount === 'string' ? parseFloat(amount) : amount
  if (isNaN(num)) return '¥0.00'
  return `¥${num.toFixed(2)}`
}
