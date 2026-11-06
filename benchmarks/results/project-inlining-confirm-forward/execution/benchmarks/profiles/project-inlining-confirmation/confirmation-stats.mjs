// Pure postprocessing; timing/report integrity validation stays in the recorder.
const median=xs=>[...xs].sort((a,b)=>a-b)[Math.floor(xs.length/2)];
export function normalizeProject(p,roles,runs){
 const old=roles.unchanged,next=roles.optimized;
 const ratios=p.pairs.map(pair=>pair[old]/pair[next]);
 const baselineMedianMs=p[old].medianMs,candidateMedianMs=p[next].medianMs;
 const baselineMedianRssMiB=p.resources[old].peakRssKiB.median/1024,candidateMedianRssMiB=p.resources[next].peakRssKiB.median/1024;
 return {name:p.name,runs,files:p.preflight[old].fileCount,baselineMedianMs,candidateMedianMs,baselineOverCandidate:baselineMedianMs/candidateMedianMs,pairedRatios:ratios,pairedMedian:median(ratios),pairedMin:Math.min(...ratios),pairedMax:Math.max(...ratios),optimizedFasterPairs:ratios.filter(r=>r>1).length,baselineMedianRssMiB,candidateMedianRssMiB,rssCandidateOverBaseline:candidateMedianRssMiB/baselineMedianRssMiB};
}
export function evaluateResults(results){
 const gm=xs=>Math.exp(xs.reduce((sum,x)=>sum+Math.log(x),0)/xs.length);
 const aggregates={ratioOfMediansGeometricMean:gm(results.map(r=>r.baselineOverCandidate)),pairedMedianGeometricMean:gm(results.map(r=>r.pairedMedian))};
 const gates={bothAggregatesAtLeast101:aggregates.ratioOfMediansGeometricMean>=1.01&&aggregates.pairedMedianGeometricMean>=1.01,allWorkloadSummariesAtLeast098:results.every(r=>r.baselineOverCandidate>=.98&&r.pairedMedian>=.98),allWorkloadMedianRssAtMost105:results.every(r=>r.rssCandidateOverBaseline<=1.05)};
 return {aggregates,gates,passes:Object.values(gates).every(Boolean)};
}
