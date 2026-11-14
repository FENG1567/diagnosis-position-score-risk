#!/usr/bin/env python3
"""Stage an authorized clinical rerun without editing frozen public results.

Only historical path string constants are translated. The published source is
unchanged; transformed runtime copies and all patient-level outputs stay private.
"""
import argparse,ast,json,os,runpy,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent

class TranslatePaths(ast.NodeTransformer):
 def __init__(self,mappings):self.mappings=mappings;self.changed=0
 def visit_Constant(self,node):
  if isinstance(node.value,str):
   normalized=node.value.replace('\\','/')
   for old,new in self.mappings:
    if normalized==old or normalized.startswith(old+'/'):
     self.changed+=1;return ast.copy_location(ast.Constant(value=new+normalized[len(old):]),node)
  return node

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('--config',type=Path,required=True);parser.add_argument('script');parser.add_argument('script_args',nargs=argparse.REMAINDER)
 args=parser.parse_args();cfg=json.loads(args.config.read_text(encoding='utf-8-sig'))
 rel=Path(args.script);original=(ROOT/rel).resolve()
 if not original.is_relative_to(ROOT/'work') or original.suffix!='.py' or not original.is_file():raise ValueError('Select a supplied work/... Python module')
 rel=original.relative_to(ROOT) # Absolute input must never bypass the private staging root.
 staging=(ROOT/cfg.get('run_root','private/reanalysis')).resolve()
 if not staging.is_relative_to(ROOT/'private'):raise ValueError('run_root must be inside this checkout/private/; patient data must stay outside tracked results')
 staging.mkdir(parents=True,exist_ok=True)
 mappings=[]
 for m in cfg.get('path_mappings',[]):
  old=m['from_prefix'].replace('\\','/').rstrip('/');new=str(m['to_prefix']).replace('\\','/').rstrip('/')
  if not Path(new).is_absolute() and not (len(new)>2 and new[1:3]==':/'):new=str((ROOT/new).resolve())
  mappings.append((old,new))
 if any('<' in new or new.startswith('/path/to/') for old,new in mappings):raise ValueError('Replace path placeholders with authorized local paths')
 mappings.append(('F:/分析专用/meta_measurement_20261103',str(staging/'legacy_private')))
 mappings=sorted(mappings,key=lambda pair:-len(pair[0]))
 rewritten=[]
 for directory in ['work','outputs']:
  for source in (ROOT/directory).rglob('*'):
   if not source.is_file() or '__pycache__' in source.parts:continue
   target=staging/source.relative_to(ROOT);target.parent.mkdir(parents=True,exist_ok=True)
   if target.exists() and source.suffix!='.py':continue # Preserve intermediates, but refresh executable code and mappings.
   if source.suffix=='.py':
    tree=ast.parse(source.read_text(encoding='utf-8-sig'));translator=TranslatePaths(mappings);tree=translator.visit(tree);ast.fix_missing_locations(tree)
    if translator.changed:target.write_text(ast.unparse(tree)+'\n',encoding='utf-8')
    else:shutil.copy2(source,target)
    rewritten.append({'file':str(source.relative_to(ROOT)),'path_constants_mapped':translator.changed})
   else:shutil.copy2(source,target)
 for k,v in cfg.get('environment',{}).items():os.environ[str(k)]=str(v)
 (staging/'path_translation_record.json').write_text(json.dumps({'script':str(rel),'source_revision':'RC02','rewritten_files':rewritten,'path_mappings':mappings},ensure_ascii=False,indent=2))
 forwarded=args.script_args[1:] if args.script_args[:1]==['--'] else args.script_args
 sys.argv=[str(staging/rel),*forwarded]
 sys.path[:0]=[str((staging/rel).parent),str(staging/'work/v2'),str(staging/'work/v3/validation')]
 os.chdir(staging)
 print('Executing authorized-data stage in private run root:',staging,flush=True)
 runpy.run_path(str(staging/rel),run_name='__main__')

if __name__=='__main__':main()
