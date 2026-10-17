import {capture,groups,config} from './common.mjs';const s=capture(); console.log(JSON.stringify({experiment:config.name,groups,source:s.workspaceSource,sourceDifference:s.sourceDifference}));
