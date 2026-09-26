// Requires the Codex bundled artifact-tool runtime. See docs/presentation.md.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL} from 'node:url';
const runtime = process.env.SCOUT_NODE_MODULES;
const skill = process.env.SCOUT_PRESENTATION_SKILL;
if (!runtime || !skill) throw new Error('Set SCOUT_NODE_MODULES and SCOUT_PRESENTATION_SKILL to bundled runtime paths.');
process.env.RUNTIME_NODE_MODULES = runtime;
const {Presentation, PresentationFile} = await import(pathToFileURL(path.join(runtime,'@oai/artifact-tool/dist/artifact_tool.mjs')));
const {finalizePresentation} = await import(pathToFileURL(path.join(skill,'container_tools/artifact_tool_utils.mjs')));
const workspaceDir = process.cwd();
const tmp = path.join(workspaceDir,'tmp/pitch');
const out = path.join(workspaceDir,'output/presentation');
await fs.mkdir(tmp,{recursive:true}); await fs.mkdir(out,{recursive:true});
const p = Presentation.create({slideSize:{width:1280,height:720}});
const slide = p.slides.add(); slide.background.fill='#F6F4EA';
const content = [
 {x:64,y:44,w:1150,h:72,size:58,bold:true,color:'#173F2E',text:'Hapus Scout'},
 {x:66,y:127,w:1140,h:48,size:28,color:'#435749',text:'Orchard inspection support for Alphonso mango teams'},
 {x:66,y:219,w:505,h:38,size:26,bold:true,color:'#173F2E',text:'The problem we are testing'},
 {x:66,y:269,w:505,h:156,size:26,color:'#273D30',text:'Workers need a consistent way to report suspicious leaf or fruit symptoms. Managers need enough evidence to decide what to inspect.'},
 {x:655,y:219,w:555,h:38,size:26,bold:true,color:'#173F2E',text:'The working journey'},
 {x:655,y:269,w:555,h:145,size:27,color:'#273D30',text:'1. Capture a photo and worker note\n2. AI observes and asks questions\n3. Manager reviews the inspection brief'},
 {x:66,y:457,w:1140,h:65,size:25,color:'#173F2E',text:'Qwen3-VL + Gradio in one Colab runtime\nExisting model weights and saved cases in Google Drive'},
 {x:66,y:556,w:1140,h:53,size:23,color:'#435749',text:'Next: agronomist evaluation, Marathi / voice usability, team permissions'},
 {x:66,y:636,w:1140,h:52,size:19,color:'#6D6345',text:'Problem hypothesis; impact unmeasured. Inspection support, not confirmed diagnosis.\nAssumes internet and an active GPU session. Live model acceptance pending.'}
];
for (const c of content) {
 const s = slide.shapes.add({geometry:'textbox',position:{left:c.x,top:c.y,width:c.w,height:c.h},fill:'none',line:{fill:'none',width:0}});
 s.text=c.text; s.text.style={typeface:'Arial',fontSize:c.size,bold:!!c.bold,color:c.color,autoFit:'none'};
}
slide.speakerNotes.textFrame.setText('Problem is a founder hypothesis; no interviews or measured ROI claimed. Existing open model weights reused; Scout app newly authored. Sources: https://huggingface.co/Qwen/Qwen3-VL-4B-Instruct ; https://www.gradio.app/guides/quickstart ; https://nhb.gov.in/report_files/mango/mango.htm . Live model acceptance is pending; update only after actual verification. Seven-minute demonstration script: docs/demo-script.md.');
const candidatePath=path.join(tmp,'candidate.pptx');
await (await PresentationFile.exportPptx(p)).save(candidatePath);
const image=await p.export({slide,format:'png',scale:1});
await fs.writeFile(path.join(tmp,'slide.png'),new Uint8Array(await image.arrayBuffer()));
await fs.writeFile(path.join(tmp,'layout.json'),await (await slide.export({format:'layout'})).text());
await fs.writeFile(path.join(tmp,'content.json'),JSON.stringify(content));
const finalPath=path.join(out,'hapus-scout-day1.pptx');
await finalizePresentation({workspaceDir,candidatePath,finalPath,
 pythonExecutable:process.env.SCOUT_PYTHON,
 integrityValidatorPath:path.join(skill,'container_tools/inspect_presentation_package_integrity.py'),
 layoutValidatorPath:path.join(skill,'container_tools/inspect_presentation_layout_geometry.py'),
 layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-heading-fit'],
 explicitTotalSlideCount:1,fontPolicy:{basis:'design',families:['Arial']},
 verifyArtifactToolImport:true,receiptPath:path.join(tmp,'validation.json')});
console.log(finalPath);
