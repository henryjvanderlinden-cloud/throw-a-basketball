from PIL import Image,ImageDraw,ImageFilter
import numpy as np
from pathlib import Path
root=Path(r'C:\Git\throw-a-basketball\artwork')
im=Image.open(root/'backboard-bonanza-v2.png').convert('RGBA'); w,h=im.size
scale=3
mask=Image.new('L',(w*scale,h*scale),0)
d=ImageDraw.Draw(mask)
def poly(points):
    d.polygon([(round(x*w/1536*scale),round(y*h/1024*scale)) for x,y in points],fill=255)
# Follow the outer silhouette of the glass frame and protruding headline.
poly([(150,114),(168,103),(1285,53),(1324,50),(1349,60),(1361,78),(1389,204),(1432,214),(1482,237),(1526,320),(1499,437),(1440,481),(1508,872),(1504,900),(1496,919),(1475,936),(1453,941),(64,923),(45,915),(34,900),(29,879),(32,856),(85,530),(52,537),(10,493),(11,478),(66,258),(72,244),(151,209),(143,181),(148,130)])
# Detached and protruding shards keep their original painted glass.
for pts in [
[(239,56),(307,5),(346,171)],
[(1370,93),(1405,23),(1460,73),(1383,163)],
[(1402,157),(1457,137),(1433,191)],
[(53,168),(75,143),(152,202),(141,231)],
[(22,674),(146,629),(84,752)],
[(1374,582),(1488,498),(1520,546),(1427,594)],
[(210,980),(250,833),(330,799),(289,920)],
[(424,958),(500,887),(468,973)],
[(506,974),(534,953),(520,994)],
[(884,923),(904,926),(923,962)],
[(900,891),(940,908),(957,978)],
[(1000,895),(1034,915),(1108,969),(1048,1019)],
]: poly(pts)
mask=mask.resize((w,h),Image.Resampling.LANCZOS)
a=np.array(mask)
rgb=np.asarray(im)[:,:,:3].astype(float)
# Preserve hanging net cords while clearing the visible gaps below the frame.
yy,xx=np.mgrid[:h,:w]; x=xx*1536/w; y=yy*1024/h
net=(x>652)&(x<845)&(y>925)&(y<1021)
brightness=rgb.max(2)
neutral=(rgb.max(2)-rgb.min(2))<85
cord=net&neutral&(brightness>180)&(rgb[:,:,0]>rgb[:,:,2]-3)
netmask=Image.fromarray((cord*255).astype('uint8'))
a=np.maximum(a,np.asarray(netmask))
im.putalpha(Image.fromarray(a))
output=root/'backboard-bonanza-transparent.png'; im.save(output)
check=Image.open(output); assert check.mode=='RGBA' and check.getextrema()[3]==(0,255)
print(output,check.size,'verified alpha')
preview=Image.new('RGBA',im.size,(35,25,55,255));preview.alpha_composite(im);preview.thumbnail((1152,768))
preview.convert('RGB').save(root/'backboard-bonanza-transparent-preview.jpg')

