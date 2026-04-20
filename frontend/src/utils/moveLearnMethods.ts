import type { MoveLearnMethod } from "@/types";

export function formatLearnMethodLabels(
  methods: MoveLearnMethod[],
  labelLearnMethod: (method: string) => string,
  levelPrefix = "Lv "
): string[] {
  if (!methods.length) {
    return [];
  }

  const levelValues = Array.from(
    new Set(
      methods
        .filter(
          (method): method is MoveLearnMethod & { level: number } =>
            method.method === "level-up" && method.level !== null
        )
        .map((method) => method.level)
    )
  ).sort((a, b) => a - b);

  const labels: string[] = [];
  if (levelValues.length) {
    labels.push(`${levelPrefix}${levelValues.join(", ")}`);
  } else if (methods.some((method) => method.method === "level-up")) {
    labels.push(labelLearnMethod("level-up"));
  }

  const seenMethods = new Set<string>();
  for (const method of methods) {
    if (method.method === "level-up" || seenMethods.has(method.method)) {
      continue;
    }
    labels.push(labelLearnMethod(method.method));
    seenMethods.add(method.method);
  }

  return labels;
}
