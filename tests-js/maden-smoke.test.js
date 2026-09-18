const assert = require('assert');
const { tokenize } = require('../src-js/maden-lexer');
const { Parser } = require('../src-js/maden-parser');
const { MadenInterpreter } = require('../src-js/maden-interpreter');

function run(source) {
  const output = [];
  const program = new Parser(tokenize(source)).parse();
  new MadenInterpreter(value => output.push(value)).run(program);
  return output;
}

function test(name, callback) {
  try {
    callback();
    console.log(`OK: ${name}`);
  } catch (error) {
    console.error(`GAGAL: ${name}`);
    throw error;
  }
}

test('fungsi dan return', () => {
  const output = run(`
    fungsi tambah(a, b) {
      kembali a + b
    }
    cetak(tambah(2, 3))
  `);
  assert.deepStrictEqual(output, ['5']);
});

test('kondisi jika dan selain', () => {
  const output = run(`
    nilai = 10
    jika nilai > 5 {
      cetak("besar")
    } selain {
      cetak("kecil")
    }
  `);
  assert.deepStrictEqual(output, ['besar']);
});

test('ulangi selama', () => {
  const output = run(`
    i = 0
    ulangi selama i < 3 {
      cetak(i)
      i = i + 1
    }
  `);
  assert.deepStrictEqual(output, ['0', '1', '2']);
});

test('boolean dan operator logika', () => {
  const output = run(`
    jika benar dan tidak salah {
      cetak("aktif")
    }
  `);
  assert.deepStrictEqual(output, ['aktif']);
});

test('error variabel tidak dikenal', () => {
  assert.throws(
    () => run('cetak(tidakAda)'),
    /Variabel 'tidakAda' tidak ditemukan/
  );
});

console.log('Semua smoke test Maden berhasil.');
