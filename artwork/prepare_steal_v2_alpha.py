from PIL import Image
import numpy as np
from pathlib import Path
src=Path(r'C:\Users\User\.codex\generated_images\01a0995d-aabb-7921-a555-2a98eedd7274\exec-41fcf5e9-c2c6-4846-a2ed-50f804ea7edb.png')
outpath=Path(r'C:\Git\throw-a-basketball\artwork\steal-purple-skull-v2.png')
im=Image.open(src).convert('RGBA')
a=np.array(im)
r,g,b=[a[:,:,i].astype(float) for i in range(3)]
key=(g>r+30)&(g>b+30)
a[key]=0
out=Image.fromarray(a);out.save(outpath)
check=Image.open(outpath)
assert check.mode=='RGBA' and check.getextrema()[3]==(0,255)
print(str(outpath), check.size,'verified alpha')
p=Image.new('RGBA',out.size,(25,32,46,255));p.alpha_composite(out);p.thumbnail((1000,1000))
p.convert('RGB').save(outpath.with_name('steal-purple-skull-v2-preview.jpg'))

