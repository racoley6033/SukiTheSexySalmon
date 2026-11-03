import {test} from 'node:test';
import assert from 'node:assert/strict';
import {CLIPS, sampleMotion} from './motion.mjs';
import {sourceRect} from './atlas.mjs';
test('all motion clips loop and exported frames stay finite and in stage margins',()=>{
  for(const clip of CLIPS){
    assert.deepEqual(sampleMotion(clip,0),sampleMotion(clip,2));
    for(let i=0;i<48;i++){
      const p=sampleMotion(clip,i/24);
      assert.ok(Object.values(p).every(Number.isFinite));
      assert.ok(Math.abs(p.x)<=95 && p.y>=-50 && p.y<=0);
      assert.ok(p.sx>0 && p.sy>0);
    }
  }
});
test('invalid clips and nonfinite time are rejected',()=>{
  assert.throws(()=>sampleMotion('walk',0));
  assert.throws(()=>sampleMotion('idle',NaN));
});
test('atlas cells cover the supplied expression layout without overlap',()=>{
  assert.deepEqual(sourceRect(1536,1024,'surprised'),{x:1024,y:512,width:512,height:512});
  assert.throws(()=>sourceRect(1535,1024,'happy'));
  assert.throws(()=>sourceRect(1536,1024,'unknown'));
});
