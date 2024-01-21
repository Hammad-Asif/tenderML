
  keyBullets = list(bullets.keys())
  valuesBullets = list(bullets.values())
  indexKeys = list(indexes.keys())
  bullets = dict(bullets)
  k = 0
  travIndex=-1
while k < len(valuesBullets):
      if k>2:
        prev=k-1
      elif k==2:
        prev=k-2
      else:
        k+=1
        continue
      while valuesBullets[k]<valuesBullets[prev] and prev>0:
        prev=prev-1
      if prev==0:
        travIndex=k-1
        indKeys=[x for x in indexKeys if x <valuesBullets[k]]
        while travIndex>=0:
          for i in range(len(indKeys)-1,0,-1):
            if indexes[indKeys[i]][0][2]==keyBullets[travIndex]:
              bullets[keyBullets[travIndex]]=indKeys[i]
              valuesBullets[travIndex]=indKeys[i]
              break
          travIndex=travIndex-1
      else:
        travIndex=k-1
        indKeys=[x for x in indexKeys if x <valuesBullets[k] and x >valuesBullets[prev]]
        # print(travIndex,prev)
        
        while travIndex>=prev:
          for i in range(len(indKeys)-1,0,-1):
            if indexes[indKeys[i]][0][2]==keyBullets[travIndex]:
              print(indexes[indKeys[i]][0][2])
              bullets[keyBullets[travIndex]]=indKeys[i]
              valuesBullets[travIndex]=indKeys[i]
              break
          travIndex=travIndex-1
        
      k+=1