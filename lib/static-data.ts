import fs from 'fs';
import path from 'path';
import type { Arena } from '@/lib/types';

// In Next.js, files in lib/ are bundled, so __dirname is not reliable.
// We use process.cwd() which is the project root in both dev and build.
const PROJECT_ROOT = process.cwd();
const ARENAS_ROOT_DIR = path.join(PROJECT_ROOT, 'Content', 'Arena', 'All Arenas');

// Use a function so paths are evaluated at runtime.
function getArenaJsonPaths() {
  return {
    zh: path.join(PROJECT_ROOT, 'Content', 'Arena', 'page.zh.json'),
    en: path.join(PROJECT_ROOT, 'Content', 'Arena', 'page.en.json'),
    common: path.join(PROJECT_ROOT, 'Content', 'Arena', 'page.common.json'),
  };
}

export type ArenaTechConfigStep = {
  number: number;
  title: string;
  subsections: Array<{ title: string; content: string[] }>;
};

export type ArenaTechConfigPayload = {
  markdown?: string;
  steps?: ArenaTechConfigStep[];
  [key: string]: unknown;
};

export type ArenaContentValue = string | ArenaTechConfigPayload;
type ArenaContentMap = Record<string, Record<string, Record<string, ArenaContentValue>>>;

let cachedArenas: Arena[] | null = null;
let cachedArenasMtimeKey = '';

type ArenaRow = {
  arena_no?: string | number;
  title?: string;
  champion?: string;
  related_references?: string;
  verification_status?: string;
  highlights?: string;
  industry?: string;
  category?: string;
  speed?: string;
  quality?: string;
  security?: string;
  cost?: string;
  challenger?: string;
};

type ArenaCommonRow = {
  arena_no?: string | number;
  video_url_zh?: string | null;
  video_url_global?: string | null;
  video_cover_image_url?: string | null;
  homepage_display_order?: string | number | null;
};

function cleanText(value: unknown): string {
  return String(value ?? '').trim();
}

function readJsonRows<T extends Record<string, unknown>>(filePath: string): T[] {
  if (!fs.existsSync(filePath)) return [];
  try {
    const parsed = JSON.parse(fs.readFileSync(filePath, 'utf-8')) as unknown;
    return Array.isArray(parsed) ? (parsed as T[]) : [];
  } catch {
    return [];
  }
}

function buildFolderMapByArenaNo(): Map<string, string> {
  const map = new Map<string, string>();
  if (!fs.existsSync(ARENAS_ROOT_DIR)) {
    return map;
  }

  const dirs = fs.readdirSync(ARENAS_ROOT_DIR, { withFileTypes: true }).filter((entry) => entry.isDirectory());
  for (const dir of dirs) {
    const match = dir.name.match(/^(\d+)-/);
    if (match) {
      map.set(match[1], dir.name);
    }
  }
  return map;
}

function hasArenaContent(folderId: string): boolean {
  if (!folderId) return false;
  const folderPath = path.join(ARENAS_ROOT_DIR, folderId);
  if (!fs.existsSync(folderPath)) return false;

  return fs.existsSync(path.join(folderPath, 'overview.zh.json'))
    || fs.existsSync(path.join(folderPath, 'overview.en.json'))
    || fs.existsSync(path.join(folderPath, 'implementation.zh.json'))
    || fs.existsSync(path.join(folderPath, 'implementation.en.json'))
    || fs.existsSync(path.join(folderPath, 'tech-configuration.zh.json'))
    || fs.existsSync(path.join(folderPath, 'tech-configuration.en.json'));
}

function buildArenasFromJson(): Arena[] {
  const jsonPaths = getArenaJsonPaths();
  const zhRows = readJsonRows<ArenaRow>(jsonPaths.zh);
  const enRows = readJsonRows<ArenaRow>(jsonPaths.en);
  const commonRows = readJsonRows<ArenaCommonRow>(jsonPaths.common);

  const folderMap = buildFolderMapByArenaNo();
  const enMap = new Map<string, ArenaRow>();
  for (const row of enRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      enMap.set(arenaNo, row);
    }
  }
  const commonMap = new Map<string, ArenaCommonRow>();
  for (const row of commonRows) {
    const arenaNo = cleanText(row.arena_no);
    if (arenaNo) {
      commonMap.set(arenaNo, row);
    }
  }

  const arenas: Arena[] = [];
  for (const row of zhRows) {
    const arenaNo = cleanText(row.arena_no);
    if (!arenaNo) continue;

    const enRow = enMap.get(arenaNo);
    const commonRow = commonMap.get(arenaNo);
    const titleZh = cleanText(row.title);
    if (!titleZh || titleZh.includes('敬请期待')) continue;

    const folderId = folderMap.get(arenaNo) || '';
    const videoUrlZh = cleanText(commonRow?.video_url_zh) || undefined;
    const videoUrlGlobal = cleanText(commonRow?.video_url_global) || undefined;
    arenas.push({
      id: arenaNo,
      folderId,
      title: {
        zh: titleZh,
        en: cleanText(enRow?.title),
      },
      category: cleanText(row.category),
      categoryEn: cleanText(enRow?.category),
      industry: cleanText(row.industry),
      industryEn: cleanText(enRow?.industry),
      verificationStatus: cleanText(row.verification_status),
      champion: cleanText(row.champion),
      championEn: cleanText(enRow?.champion),
      challenger: cleanText(row.challenger),
      challengerEn: cleanText(enRow?.challenger),
      highlights: cleanText(row.highlights),
      highlightsEn: cleanText(enRow?.highlights),
      relatedReferences: cleanText(row.related_references) || undefined,
      relatedReferencesEn: cleanText(enRow?.related_references) || undefined,
      metrics: {
        speed: cleanText(row.speed),
        quality: cleanText(row.quality),
        security: cleanText(row.security),
        cost: cleanText(row.cost),
      },
      videoUrlZh,
      videoUrlGlobal,
      videoCoverImageUrl: cleanText(commonRow?.video_cover_image_url) || undefined,
      hasContent: hasArenaContent(folderId),
    });
  }

  return arenas.sort((a, b) => Number(a.id) - Number(b.id));
}

function getArenasMtimeKey(): string {
  const jsonPaths = getArenaJsonPaths();
  const zhMtime = fs.existsSync(jsonPaths.zh) ? fs.statSync(jsonPaths.zh).mtimeMs : 0;
  const enMtime = fs.existsSync(jsonPaths.en) ? fs.statSync(jsonPaths.en).mtimeMs : 0;
  const commonMtime = fs.existsSync(jsonPaths.common) ? fs.statSync(jsonPaths.common).mtimeMs : 0;
  return `${zhMtime}|${enMtime}|${commonMtime}`;
}

export async function getAllArenasFromStaticData(): Promise<Arena[]> {
  const mtimeKey = getArenasMtimeKey();
  if (cachedArenas && cachedArenasMtimeKey === mtimeKey) {
    return cachedArenas;
  }

  cachedArenas = buildArenasFromJson();
  cachedArenasMtimeKey = mtimeKey;
  return cachedArenas;
}

function parseDisplayOrder(value: unknown): number | null {
  if (typeof value === 'number' && Number.isFinite(value)) {
    return Math.trunc(value);
  }
  if (typeof value === 'string') {
    const trimmed = value.trim();
    if (!trimmed) return null;
    const parsed = Number(trimmed);
    if (Number.isFinite(parsed)) {
      return Math.trunc(parsed);
    }
  }
  return null;
}

export async function getHomepageDisplayArenaIdsFromStaticData(): Promise<string[]> {
  const jsonPaths = getArenaJsonPaths();
  const commonRows = readJsonRows<ArenaCommonRow>(jsonPaths.common);

  return commonRows
    .map((row) => ({
      arenaNo: cleanText(row.arena_no),
      order: parseDisplayOrder(row.homepage_display_order),
    }))
    .filter((row) => row.arenaNo && row.order !== null)
    .sort((a, b) => Number(a.order) - Number(b.order))
    .map((row) => row.arenaNo);
}

export async function getArenaContentFromStaticData(
  folderId: string,
  tabKey: string,
  locale: string
): Promise<ArenaContentValue | null> {
  const normalizedLocale = locale === 'zh' ? 'zh' : 'en';
  const tabJsonPath = path.join(
    ARENAS_ROOT_DIR,
    folderId,
    `${tabKey}.${normalizedLocale}.json`
  );
  if (!fs.existsSync(tabJsonPath)) {
    return null;
  }
  try {
    return JSON.parse(fs.readFileSync(tabJsonPath, 'utf-8')) as ArenaContentValue;
  } catch (error) {
    console.error(`[static-data] Failed to parse tab JSON: ${tabJsonPath}`, error);
    return null;
  }
}
