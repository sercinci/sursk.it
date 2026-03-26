export interface TypeStyle {
  background: string;
  color: string;
  border: string;
}

export const TYPE_STYLES: Record<string, TypeStyle> = {
  normal: { background: "#9a9a9a", color: "#f7f7f7", border: "#888888" },
  fighting: { background: "#f08000", color: "#ffffff", border: "#dc7000" },
  flying: { background: "#689cd0", color: "#f5fbff", border: "#588cc0" },
  poison: { background: "#9040c0", color: "#ffffff", border: "#8132b0" },
  ground: { background: "#915121", color: "#ffffff", border: "#7f461b" },
  rock: { background: "#afa981", color: "#ffffff", border: "#9f9973" },
  bug: { background: "#89a40f", color: "#ffffff", border: "#78900c" },
  ghost: { background: "#704170", color: "#ffffff", border: "#613461" },
  steel: { background: "#60a1b8", color: "#ffffff", border: "#4f90a8" },
  fire: { background: "#e62829", color: "#ffffff", border: "#d01f20" },
  water: { background: "#2980ef", color: "#ffffff", border: "#1f70df" },
  grass: { background: "#3fa129", color: "#ffffff", border: "#328820" },
  electric: { background: "#fac000", color: "#513f00", border: "#e3ad00" },
  psychic: { background: "#ef4179", color: "#ffffff", border: "#de2f69" },
  ice: { background: "#3fc8ef", color: "#ffffff", border: "#2ab4dd" },
  dragon: { background: "#5060e1", color: "#ffffff", border: "#4352cc" },
  dark: { background: "#50413f", color: "#ffffff", border: "#433533" },
  fairy: { background: "#ef70ef", color: "#ffffff", border: "#de5fde" }
};

const DEFAULT_TYPE_STYLE: TypeStyle = {
  background: "#5c8ea1",
  color: "#ffffff",
  border: "#4b7b8d"
};

export function getTypeChipStyle(type: string) {
  const entry = TYPE_STYLES[type.toLowerCase()] ?? DEFAULT_TYPE_STYLE;
  return {
    backgroundColor: entry.background,
    color: entry.color,
    borderColor: entry.border
  };
}
