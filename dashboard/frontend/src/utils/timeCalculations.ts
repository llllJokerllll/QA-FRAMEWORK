export const calculateTimeSaved = (executions: number) => {
  const automatedTime = executions * 0.5 // 30 segundos por test automatizado
  const manualTime = executions * 10 // 10 minutos por test manual
  const saved = manualTime - automatedTime
  return {
    hours: Math.floor(saved / 60),
    minutes: Math.round(saved % 60),
    total: saved
  }
}
