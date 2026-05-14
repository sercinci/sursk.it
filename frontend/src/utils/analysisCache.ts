import type { Pokemon } from "@/types";
import type { MatchupAnalysis, AnalysisOptions } from "@/services/openai";

const CACHE_KEY = "sursk.it:matchup-cache";
const MAX_ENTRIES = 20;

export interface CachedAnalysis {
  id: string;
  timestamp: number;
  myTeam: Pokemon[];
  oppTeam: Pokemon[];
  analysis: MatchupAnalysis;
  options?: AnalysisOptions;
  duration?: number;
  source?: "local" | "xcore";
}

export function saveAnalysis(data: Omit<CachedAnalysis, "id">): CachedAnalysis {
  const entry: CachedAnalysis = { id: crypto.randomUUID(), ...data };
  const updated = [entry, ...loadAllAnalyses()].slice(0, MAX_ENTRIES);
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(updated));
  } catch {
    // localStorage quota exceeded — silently ignore
  }
  return entry;
}

export function loadAllAnalyses(): CachedAnalysis[] {
  try {
    const raw = localStorage.getItem(CACHE_KEY);
    return raw ? (JSON.parse(raw) as CachedAnalysis[]) : [];
  } catch {
    return [];
  }
}

export function deleteAnalysis(id: string): void {
  try {
    localStorage.setItem(CACHE_KEY, JSON.stringify(loadAllAnalyses().filter(e => e.id !== id)));
  } catch { /* ignore */ }
}
