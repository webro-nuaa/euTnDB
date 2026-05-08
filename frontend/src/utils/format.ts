import dayjs from 'dayjs'

export function formatDate(date: string | Date, format = 'YYYY-MM-DD HH:mm:ss'): string {
  return dayjs(date).format(format)
}

export function formatNumber(num: number): string {
  return num.toLocaleString()
}

export function formatSequence(seq: string, lineLength = 80): string {
  const lines: string[] = []
  for (let i = 0; i < seq.length; i += lineLength) {
    lines.push(seq.slice(i, i + lineLength))
  }
  return lines.join('\n')
}

export function formatGcContent(gc: number): string {
  return `${gc.toFixed(2)}%`
}

export function formatLength(length: number): string {
  if (length >= 1000000) {
    return `${(length / 1000000).toFixed(2)} Mb`
  } else if (length >= 1000) {
    return `${(length / 1000).toFixed(2)} Kb`
  }
  return `${length} bp`
}
