export interface StatusMap {
  [key: number]: string
}

export interface StatusTypeMap {
  [key: number]: 'success' | 'warning' | 'info' | 'danger' | 'primary' | ''
}

export function useStatusMap(statusMap: StatusMap, typeMap?: StatusTypeMap) {
  const getStatusText = (status: number): string => {
    return statusMap[status] || '未知'
  }

  const getStatusType = (status: number): 'success' | 'warning' | 'info' | 'danger' | 'primary' | '' => {
    if (typeMap) {
      return typeMap[status] || ''
    }
    
    const defaultTypeMap: StatusTypeMap = {
      0: 'info',
      1: 'warning',
      2: 'success',
      3: 'primary',
      4: 'danger',
      5: 'danger'
    }
    return defaultTypeMap[status] || ''
  }

  return {
    getStatusText,
    getStatusType
  }
}
