import {capture,config} from './common-screen.mjs';console.log(JSON.stringify({name:config.name,roles:config.canonicalRoles,snapshot:capture().workspaceSource}));
