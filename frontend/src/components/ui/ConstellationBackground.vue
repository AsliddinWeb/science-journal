<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const canvasRef = ref<HTMLCanvasElement | null>(null)
let animationId = 0

interface Particle {
  x: number
  y: number
  vx: number
  vy: number
  radius: number
}

onMounted(() => {
  const canvas = canvasRef.value
  if (!canvas) return
  const ctx = canvas.getContext('2d')
  if (!ctx) return

  let particles: Particle[] = []
  const PARTICLE_COUNT = 80
  const MAX_DIST = 140  // distance to draw connecting line

  function resize() {
    canvas.width = window.innerWidth
    canvas.height = window.innerHeight
  }

  function init() {
    particles = []
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      particles.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        radius: Math.random() * 1.5 + 0.8,
      })
    }
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    // Update + draw particles
    for (const p of particles) {
      p.x += p.vx
      p.y += p.vy

      // bounce off edges
      if (p.x < 0 || p.x > canvas.width) p.vx *= -1
      if (p.y < 0 || p.y > canvas.height) p.vy *= -1

      ctx.fillStyle = 'rgba(189, 210, 255, 0.8)'
      ctx.beginPath()
      ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2)
      ctx.fill()
    }

    // Connect nearby particles with lines
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x
        const dy = particles[i].y - particles[j].y
        const dist = Math.sqrt(dx * dx + dy * dy)
        if (dist < MAX_DIST) {
          const opacity = (1 - dist / MAX_DIST) * 0.4
          ctx.strokeStyle = `rgba(144, 179, 255, ${opacity})`
          ctx.lineWidth = 0.6
          ctx.beginPath()
          ctx.moveTo(particles[i].x, particles[i].y)
          ctx.lineTo(particles[j].x, particles[j].y)
          ctx.stroke()
        }
      }
    }

    animationId = requestAnimationFrame(draw)
  }

  resize()
  init()
  draw()

  window.addEventListener('resize', () => {
    resize()
    init()
  })
})

onUnmounted(() => {
  if (animationId) cancelAnimationFrame(animationId)
})
</script>

<template>
  <div class="pointer-events-none fixed inset-0 z-0">
    <canvas ref="canvasRef" class="h-full w-full" />
    <!-- Radial gradient overlay for depth -->
    <div class="absolute inset-0 bg-gradient-radial from-primary-900/30 via-transparent to-journal-950/40" />
  </div>
</template>

<style scoped>
.bg-gradient-radial {
  background: radial-gradient(circle at center, var(--tw-gradient-stops));
}
</style>
