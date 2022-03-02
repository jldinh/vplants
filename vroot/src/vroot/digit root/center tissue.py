from celltissue import open_tissue

f=open_tissue("mockup02_shortcapped",'r')
t,pos,info=f.read()
f.close()

#translation pour centrer le tissu
cent=pos.centroid(pos)
pos-=cent

f=open_tissue("mockup02_shortcapped",'w')
f.write(t,pos,info)
f.close()
