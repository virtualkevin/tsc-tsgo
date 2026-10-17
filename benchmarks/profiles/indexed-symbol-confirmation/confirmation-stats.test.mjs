import test from 'node:test';
import assert from 'node:assert/strict';
import {normalizeProject,evaluateResults} from './confirmation-stats.mjs';
const project={name:'fixture',baseline:{medianMs:100},candidate:{medianMs:100},preflight:{baseline:{fileCount:7},candidate:{fileCount:7}},resources:{baseline:{peakRssKiB:{median:120*1024}},candidate:{peakRssKiB:{median:110*1024}}},pairs:[{baseline:10,candidate:100},{baseline:100,candidate:10},{baseline:200,candidate:300}]};
test('reversed raw roles preserve canonical times, pair order and RSS direction',()=>{
 const forward=normalizeProject(project,{unchanged:'baseline',indexed:'candidate'},3);
 const reverse={...project,baseline:project.candidate,candidate:project.baseline,resources:{baseline:project.resources.candidate,candidate:project.resources.baseline},pairs:project.pairs.map(p=>({baseline:p.candidate,candidate:p.baseline}))};
 const normalized=normalizeProject(reverse,{unchanged:'candidate',indexed:'baseline'},3);
 assert.deepEqual(normalized,forward);assert.deepEqual(forward.pairedRatios,[.1,10,2/3]);assert.equal(forward.baselineOverCandidate,1);assert.equal(forward.pairedMedian,2/3);assert.equal(forward.rssCandidateOverBaseline,11/12);assert.equal(forward.indexedFasterPairs,1);
});
test('a favorable aggregate cannot hide a workload regression or memory breach',()=>{
 const rows=Array.from({length:4},()=>({baselineOverCandidate:1.2,pairedMedian:1.2,rssCandidateOverBaseline:1}));
 assert.equal(evaluateResults(rows).passes,true);
 rows[3].pairedMedian=.97;let x=evaluateResults(rows);assert.equal(x.gates.bothAggregatesAtLeast101,true);assert.equal(x.gates.allWorkloadSummariesAtLeast098,false);assert.equal(x.passes,false);
 rows[3].pairedMedian=1.2;rows[3].rssCandidateOverBaseline=1.051;x=evaluateResults(rows);assert.equal(x.gates.bothAggregatesAtLeast101,true);assert.equal(x.gates.allWorkloadMedianRssAtMost105,false);assert.equal(x.passes,false);
});
test('both aggregate summaries must pass independently',()=>{
 const rows=Array.from({length:4},()=>({baselineOverCandidate:1.1,pairedMedian:1.009,rssCandidateOverBaseline:1}));
 const x=evaluateResults(rows);assert.ok(x.aggregates.ratioOfMediansGeometricMean>1.01);assert.ok(x.aggregates.pairedMedianGeometricMean<1.01);assert.equal(x.passes,false);
});
