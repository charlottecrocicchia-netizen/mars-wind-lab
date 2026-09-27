// Associations describe published proposals; none establishes a launch site.
export const groupKey = value => String(value ?? '').trim().replace(/^group\s+/i, '');
export const sampleGroup = sample => `group ${groupKey(sample.ejection_group)}`;
export function candidateRelations(group, craters) {
  if (!group) return [];
  return craters.flatMap(crater => {
    if (group.preferred_candidate === crater.name) return [{crater, kind:'preferred', condition:'Preferred in the group compilation; not confirmed.'}];
    if (crater.groups.includes(group.group)) return [{crater, kind:'linked', condition:'Linked by the cited source study; not confirmed.'}];
    if (crater.name === 'Unnamed') return [];
    const escaped=crater.name.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const condition=group.alternatives.find(text => new RegExp(`\\b${escaped}\\b`, 'i').test(text));
    return condition ? [{crater, kind:'alternative', condition}] : [];
  });
}
