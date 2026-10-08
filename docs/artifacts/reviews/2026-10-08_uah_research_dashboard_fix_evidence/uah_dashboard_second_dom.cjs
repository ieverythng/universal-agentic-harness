const fs = require('node:fs');
const vm = require('node:vm');
const path = process.argv[2] || '/home/juanbeck/universal-agentic-harness/docs/research/uah_research_dashboard.html';
const source = fs.readFileSync(path, 'utf8');
const decode = s => s.replace(/<[^>]*>/g, '').replace(/&lt;/g, '<').replace(/&gt;/g, '>').replace(/&amp;/g, '&');
const tables = [...source.matchAll(/<table>([\s\S]*?)<\/table>/g)].map(t => {
  const cells = [...t[1].matchAll(/<tbody>([\s\S]*?)<\/tbody>/g)].flatMap(m => [...m[1].matchAll(/<tr>([\s\S]*?)<\/tr>/g)]).map(m => {
    const td = [...m[1].matchAll(/<td>([\s\S]*?)<\/td>/g)].map(c => ({textContent: decode(c[1])}));
    return {textContent: td.map(c => c.textContent).join(''), hidden:false, querySelectorAll: () => td};
  });
  return {querySelector:()=>({textContent:decode(t[1].match(/<th>([\s\S]*?)<\/th>/)?.[1] || '')}), querySelectorAll:()=>cells};
});
const buttons = [...source.matchAll(/data-kind="([^"]+)"/g)].map(m => ({dataset:{kind:m[1]}, events:{}, addEventListener(type, cb){this.events[type]=cb}, setAttribute(){}}));
const input = () => ({value:'', events:{}, addEventListener(type,cb){this.events[type]=cb}});
const search=input(), gate=input(); gate.value='all';
const count={textContent:''};
const elements={'research-tabs':{querySelectorAll:()=>buttons},'research-search':search,'research-gate':gate,'research-count':count};
const document={querySelectorAll:()=>tables,getElementById:id=>elements[id]};
const code=[...source.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
try {
  vm.runInNewContext(code, {document});
  console.log(JSON.stringify({path,initial:count.textContent}));
  for (const button of buttons) {button.events.click(); console.log(JSON.stringify({kind:button.dataset.kind,count:count.textContent}));}
  buttons[0].events.click();
  for (let i=0;i<=6;i++){gate.value=`H${i}`;gate.events.change();console.log(JSON.stringify({gate:gate.value,count:count.textContent}));}
  gate.value='all'; gate.events.change();
  search.value='no-match-unreal-string';search.events.input();console.log(JSON.stringify({query:search.value,count:count.textContent}));
  search.value='Vendor claims';search.events.input();console.log(JSON.stringify({query:search.value,count:count.textContent,summaryExists:source.includes('Vendor claims')}));
} catch(error) {console.log(JSON.stringify({path,error:String(error)}));process.exitCode=1;}
