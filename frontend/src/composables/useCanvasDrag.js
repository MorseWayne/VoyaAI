/**
 * Composable for managing canvas free-drag layout positions.
 * Auto-generates layout if not already present in the day.
 */

const CARD_W = 260
const CARD_H = 180
const MIN_X = 10
const MIN_Y = 10
const BASE_X = 40
const BASE_Y = 40
const GAP_Y = 200

export function useCanvasDrag() {
  /**
   * Generate default snake-like layout positions for a given count.
   * Adapts to container width for responsive layout.
   */
  function generateDefaultLayout(count, containerWidth = 1060) {
    const usableWidth = Math.max(containerWidth - MIN_X * 2, CARD_W + 40)
    const cols = Math.max(1, Math.min(3, Math.floor(usableWidth / (CARD_W + 60))))
    const gapX = cols > 1 ? (usableWidth - CARD_W) / (cols - 1) : 0

    const layout = []
    for (let i = 0; i < count; i++) {
      const row = Math.floor(i / cols)
      const col = (row % 2 === 0) ? (i % cols) : (cols - 1 - (i % cols))
      layout.push({
        x: BASE_X + col * gapX,
        y: BASE_Y + row * GAP_Y,
      })
    }
    return layout
  }

  /**
   * Clamp a position to stay within visible bounds.
   */
  function clampPosition(pos, containerWidth = 1060) {
    return {
      x: Math.max(MIN_X, Math.min(pos.x, containerWidth - CARD_W - MIN_X)),
      y: Math.max(MIN_Y, pos.y),
    }
  }

  /**
   * Ensure layout positions exist for every location in the day.
   * Generates a snake-like default layout if positions are missing.
   * Clamps any out-of-bounds positions.
   */
  function ensureLayout(day, containerWidth = 1060) {
    const count = (day.segments?.length || 0) + 1
    if (!day.layout) day.layout = []

    // Fill in missing positions with default layout
    if (day.layout.length < count) {
      const defaults = generateDefaultLayout(count, containerWidth)
      for (let i = day.layout.length; i < count; i++) {
        day.layout.push(defaults[i])
      }
    }

    // Trim excess positions
    while (day.layout.length > count) {
      day.layout.pop()
    }

    // Clamp all positions to valid bounds
    for (let i = 0; i < day.layout.length; i++) {
      if (day.layout[i]) {
        day.layout[i] = clampPosition(day.layout[i], containerWidth)
      }
    }

    return day.layout
  }

  /**
   * Force regenerate the layout with default positions (reset).
   */
  function resetLayout(day, containerWidth = 1060) {
    const count = (day.segments?.length || 0) + 1
    day.layout = generateDefaultLayout(count, containerWidth)
    return day.layout
  }

  return { ensureLayout, resetLayout, clampPosition, CARD_W, CARD_H, MIN_X, MIN_Y }
}
