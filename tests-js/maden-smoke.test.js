const assert = require('assert');
const { tokenize } = require('../src-js/maden-lexer');
const { Parser } = require('../src-js/maden-parser-array');
const { MadenInterpreter } = require('../src-js/maden-interpreter-array');
function run(source){const output=[];new MadenInterpreter(v=>output.push(v)).run(new Parser(tokenize(source)).parse());return output;}
function test(name,fn){try{fn();console.log(`OK: ${name}`);}catch(e){console.error(`GAGAL: ${name}`);throw e;}}
test('fungsi dan return',()=>assert.deepStrictEqual(run('fungsi tambah(a,b){ kembali a+b } cetak(tambah(2,3))'),['5']));
test('kondisi',()=>assert.deepStrictEqual(run('nilai=10 jika nilai>5 { cetak("besar") } selain { cetak("kecil") }'),['besar']));
test('ulangi selama',()=>assert.deepStrictEqual(run('i=0 ulangi selama i<3 { cetak(i) i=i+1 }'),['0','1','2']));
test('array dan untuk setiap',()=>assert.deepStrictEqual(run('angka=[1,2,3] untuk setiap nilai dalam angka { cetak(nilai) }'),['1','2','3']));
test('array dengan ekspresi',()=>assert.deepStrictEqual(run('data=[1+2,3*4] untuk setiap nilai dalam data { cetak(nilai) }'),['3','12']));
test('error variabel',()=>assert.throws(()=>run('cetak(tidakAda)'),/Variabel 'tidakAda' tidak ditemukan/));
console.log('Semua smoke test Maden berhasil.');
