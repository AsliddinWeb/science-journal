/**
 * Professional color palettes for a scientific journal.
 *
 * Each theme provides:
 *   - `primary`: 11 RGB triplets (50..950) — the accent / action color.
 *   - `journal`: 11 RGB triplets (50..950) — the darker sibling used for
 *     headers, sidebars, and heading text.
 *
 * Palettes are hand-balanced for print-worthy readability: deep, desaturated
 * primaries (nothing too "web-toy" bright) and a calm slate/navy journal
 * pair that keeps body text and chrome legible in both light and dark modes.
 *
 * Inspired by established academic publishers (Oxford UP, Nature, Wiley,
 * Elsevier, Cell, IEEE, PLOS, Cambridge UP, Springer, The Royal Society).
 */

export type Shade = '50' | '100' | '200' | '300' | '400' | '500' | '600' | '700' | '800' | '900' | '950'
export type Palette = Record<Shade, string>

export interface Theme {
  id: string
  label: string
  description?: string
  primary: Palette
  journal: Palette
}

// ─── Shared palettes ────────────────────────────────────────────────────────
const SLATE: Palette = {
  '50':  '248 250 252',
  '100': '241 245 249',
  '200': '226 232 240',
  '300': '203 213 225',
  '400': '148 163 184',
  '500': '100 116 139',
  '600': '71 85 105',
  '700': '51 65 85',
  '800': '30 41 59',
  '900': '15 23 42',
  '950': '2 6 23',
}

const NAVY: Palette = {
  '50':  '238 242 251',
  '100': '214 224 244',
  '200': '175 194 230',
  '300': '126 155 207',
  '400': '81 116 177',
  '500': '52 84 144',
  '600': '37 64 117',
  '700': '27 50 93',
  '800': '19 39 75',
  '900': '12 27 56',
  '950': '6 14 32',
}

// ─── Themes ─────────────────────────────────────────────────────────────────

export const THEMES: Theme[] = [
  {
    id: 'oxford',
    label: 'Oxford — Scholarly Navy',
    description: 'Oxford-blue authority paired with warm slate. The default.',
    primary: {
      '50':  '238 244 252',
      '100': '215 227 245',
      '200': '174 199 230',
      '300': '124 161 207',
      '400': '77 121 178',
      '500': '44 88 144',
      '600': '30 67 117',
      '700': '21 51 93',
      '800': '14 39 75',
      '900': '9 28 56',
      '950': '4 15 34',
    },
    journal: SLATE,
  },
  {
    id: 'nature',
    label: 'Nature — Publishing Blue',
    description: 'Nature-journal deep blue. Confident, print-grade.',
    primary: {
      '50':  '236 244 252',
      '100': '209 227 247',
      '200': '162 199 239',
      '300': '108 166 227',
      '400': '63 131 206',
      '500': '31 99 181',
      '600': '17 75 151',
      '700': '10 57 122',
      '800': '6 44 99',
      '900': '4 34 79',
      '950': '2 19 47',
    },
    journal: SLATE,
  },
  {
    id: 'cambridge',
    label: 'Cambridge — Sage & Navy',
    description: 'Muted Cambridge sage — quiet, academic, modern.',
    primary: {
      '50':  '241 246 245',
      '100': '219 233 230',
      '200': '179 211 205',
      '300': '129 181 173',
      '400': '83 147 139',
      '500': '56 115 108',
      '600': '43 95 89',
      '700': '34 77 72',
      '800': '28 62 58',
      '900': '22 50 47',
      '950': '11 28 26',
    },
    journal: NAVY,
  },
  {
    id: 'cell',
    label: 'Cell — Classic Crimson',
    description: 'Heritage burgundy of landmark biomedical journals.',
    primary: {
      '50':  '252 241 242',
      '100': '249 222 223',
      '200': '242 185 187',
      '300': '229 138 141',
      '400': '210 86 90',
      '500': '180 50 53',
      '600': '153 33 37',
      '700': '125 27 30',
      '800': '101 22 25',
      '900': '80 18 20',
      '950': '42 8 10',
    },
    journal: {
      '50':  '250 250 249',
      '100': '245 245 244',
      '200': '231 229 228',
      '300': '214 211 209',
      '400': '168 162 158',
      '500': '120 113 108',
      '600': '87 83 78',
      '700': '68 64 60',
      '800': '41 37 36',
      '900': '28 25 23',
      '950': '12 10 9',
    },
  },
  {
    id: 'elsevier',
    label: 'Elsevier — Orange & Navy',
    description: 'Signal orange with deep publishing navy.',
    primary: {
      '50':  '255 245 235',
      '100': '253 228 198',
      '200': '251 197 138',
      '300': '249 162 82',
      '400': '245 126 36',
      '500': '221 97 16',
      '600': '190 78 12',
      '700': '156 62 11',
      '800': '126 51 13',
      '900': '103 42 14',
      '950': '56 20 4',
    },
    journal: NAVY,
  },
  {
    id: 'ieee',
    label: 'IEEE — Engineering Blue',
    description: 'Precise, technical, high-contrast blue.',
    primary: {
      '50':  '237 245 254',
      '100': '213 231 253',
      '200': '172 208 251',
      '300': '124 180 247',
      '400': '79 148 239',
      '500': '41 116 221',
      '600': '27 92 194',
      '700': '20 75 163',
      '800': '16 61 132',
      '900': '12 48 105',
      '950': '6 28 66',
    },
    journal: SLATE,
  },
  {
    id: 'wiley',
    label: 'Wiley — Navy & Gold',
    description: 'Academic gold headlines on deep blue chrome.',
    primary: {
      '50':  '253 247 231',
      '100': '249 237 196',
      '200': '241 217 136',
      '300': '232 191 76',
      '400': '222 163 30',
      '500': '197 137 14',
      '600': '163 109 9',
      '700': '128 84 7',
      '800': '102 67 7',
      '900': '85 57 10',
      '950': '47 30 2',
    },
    journal: NAVY,
  },
  {
    id: 'plos',
    label: 'PLOS — Open Teal',
    description: 'Open-access teal, friendly but formal.',
    primary: {
      '50':  '238 251 249',
      '100': '206 245 240',
      '200': '158 230 223',
      '300': '98 208 198',
      '400': '54 180 170',
      '500': '26 149 141',
      '600': '19 120 114',
      '700': '17 96 92',
      '800': '16 77 74',
      '900': '15 64 61',
      '950': '5 38 36',
    },
    journal: NAVY,
  },
  {
    id: 'royal',
    label: 'Royal Society — Forest & Gold',
    description: 'Heritage dark green with warm accent.',
    primary: {
      '50':  '237 247 240',
      '100': '215 237 222',
      '200': '169 218 184',
      '300': '117 192 142',
      '400': '66 161 103',
      '500': '38 132 80',
      '600': '26 105 64',
      '700': '21 84 52',
      '800': '17 67 43',
      '900': '14 55 37',
      '950': '6 33 23',
    },
    journal: {
      '50':  '250 250 249',
      '100': '245 245 244',
      '200': '231 229 228',
      '300': '214 211 209',
      '400': '168 162 158',
      '500': '120 113 108',
      '600': '87 83 78',
      '700': '68 64 60',
      '800': '41 37 36',
      '900': '28 25 23',
      '950': '12 10 9',
    },
  },
  {
    id: 'graphite',
    label: 'Graphite — Minimal',
    description: 'Neutral black-and-gray. Content above all.',
    primary: {
      '50':  '244 244 245',
      '100': '228 228 231',
      '200': '212 212 216',
      '300': '161 161 170',
      '400': '113 113 122',
      '500': '82 82 91',
      '600': '63 63 70',
      '700': '51 51 56',
      '800': '39 39 42',
      '900': '24 24 27',
      '950': '9 9 11',
    },
    journal: SLATE,
  },
]

export const DEFAULT_THEME_ID = 'oxford'

export function findTheme(id: string | null | undefined): Theme {
  return THEMES.find(t => t.id === id) ?? THEMES.find(t => t.id === DEFAULT_THEME_ID)!
}

/**
 * Apply a theme by writing its RGB triplets as CSS custom properties on the
 * <html> element. Tailwind consumes them via `rgb(var(--color-primary-X) / alpha)`.
 */
export function applyTheme(theme: Theme) {
  const root = document.documentElement
  const shades: Shade[] = ['50','100','200','300','400','500','600','700','800','900','950']
  for (const s of shades) {
    root.style.setProperty(`--color-primary-${s}`, theme.primary[s])
    root.style.setProperty(`--color-journal-${s}`, theme.journal[s])
  }
  root.dataset.theme = theme.id
}
