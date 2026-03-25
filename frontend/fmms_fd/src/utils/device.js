export function  isLikelyMobile() {
  if (typeof window === 'undefined') {
    return false
  }

  const ua = window.navigator.userAgent || ''
  const mobilePattern = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i
  const byUA = mobilePattern.test(ua)
  const byTouch = window.matchMedia('(pointer: coarse)').matches && window.innerWidth <= 1024
  const byWidth = window.innerWidth <= 768

  return byUA || byTouch || byWidth
}
