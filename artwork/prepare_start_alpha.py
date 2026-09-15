from PIL import Image
import numpy as np
from pathlib import Path
src=Path(r'C:\Users\User\.codex\generated_images\01a0995d-aabb-7921-a555-2a98eedd7274\exec-41dd4ca2-049a-40d7-a64f-21210f323f1f.png')
outpath=Path(r'C:\Git\throw-a-basketball\artwork\start-orange-basketball.png')
im=Image.open(src).convert('RGBA')
a=np.array(im)
r,g,b=[a[:,:,i].astype(float) for i in range(3)]
key=(r>100)&(b>g+45)&(b>90)
a[key,3]=0
a[key,:3]=0
out=Image.fromarray(a)
out.save(outpath)
check=Image.open(outpath)
assert check.mode=='RGBA' and check.getextrema()[3]==(0,255)
print(str(outpath),check.size,'verified transparent alpha')
preview=Image.new('RGBA',out.size,(25,32,46,255));preview.alpha_composite(out)
preview.thumbnail((1000,1000))
preview.convert('RGB').save(outpath.with_name('start-orange-basketball-preview.jpg'))
