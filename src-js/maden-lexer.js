const TokenType = {
  FUNGSI: "FUNGSI",
  KEMBALI: "KEMBALI",
  CETAK: "CETAK",
  JIKA: "JIKA",
  SELAIN: "SELAIN",
  ULANGI: "ULANGI",
  SELAMA: "SELAMA",
  UNTUK: "UNTUK",
  SETIAP: "SETIAP",
  DALAM: "DALAM",
  BENAR: "BENAR",
  SALAH: "SALAH",
  KOSONG: "KOSONG",
  DAN: "DAN",
  ATAU: "ATAU",
  TIDAK: "TIDAK",

  IDENTIFIER: "IDENTIFIER",
  ANGKA: "ANGKA",
  TEKS: "TEKS",

  TAMBAH: "TAMBAH",
  KURANG: "KURANG",
  KALI: "KALI",
  BAGI: "BAGI",
  MOD: "MOD",

  KURANG_BESAR: "KURANG_BESAR",
  KURANG_KECIL: "KURANG_KECIL",
  LEBIH_BESAR: "LEBIH_BESAR",
  LEBIH_KECIL: "LEBIH_KECIL",
  LEBIH_BESAR_SAMA: "LEBIH_BESAR_SAMA",
  LEBIH_KECIL_SAMA: "LEBIH_KECIL_SAMA",
  SAMA_DENGAN: "SAMA_DENGAN",
  TIDAK_SAMA: "TIDAK_SAMA",

  KURUNG_BUKA: "KURUNG_BUKA",
  KURUNG_TUTUP: "KURUNG_TUTUP",
  BLOK_BUKA: "BLOK_BUKA",
  BLOK_TUTUP: "BLOK_TUTUP",
  KOMA: "KOMA",
  TITIK_KOMA: "TITIK_KOMA",
  SAMA: "SAMA",

  NEWLINE: "NEWLINE",
  EOF: "EOF",
};

class Token {
  constructor(type, value, line, column) {
    this.type = type;
    this.value = value;
    this.line = line;
    this.column = column;
  }
}

function tokenize(source) {
  const tokens = [];
  let i = 0;
  let line = 1;
  let column = 1;

  const keywords = {
    fungsi: TokenType.FUNGSI,
    kembali: TokenType.KEMBALI,
    cetak: TokenType.CETAK,
    jika: TokenType.JIKA,
    selain: TokenType.SELAIN,
    ulangi: TokenType.ULANGI,
    selama: TokenType.SELAMA,
    untuk: TokenType.UNTUK,
    setiap: TokenType.SETIAP,
    dalam: TokenType.DALAM,
    benar: TokenType.BENAR,
    salah: TokenType.SALAH,
    kosong: TokenType.KOSONG,
    dan: TokenType.DAN,
    atau: TokenType.ATAU,
    tidak: TokenType.TIDAK,
    not: TokenType.TIDAK,
  };

  while (i < source.length) {
    const ch = source[i];

    if (ch === ' ' || ch === '\t' || ch === '\r') {
      i++; column++; continue;
    }

    if (ch === '\n') {
      tokens.push(new Token(TokenType.NEWLINE, '\n', line, column));
      i++; line++; column = 1; continue;
    }

    if (ch === '"' || ch === "'") {
      const quote = ch;
      let value = '';
      i++; column++;
      while (i < source.length && source[i] !== quote) {
        if (source[i] === '\\') {
          i++; column++;
          if (i >= source.length) {
            throw new Error(`String tidak ditutup di baris ${line}, kolom ${column}`);
          }
          const escaped = source[i];
          value += {
            n: '\n',
            t: '\t',
            r: '\r',
            '\\': '\\',
            '"': '"',
            "'": "'",
          }[escaped] ?? escaped;
          i++; column++; continue;
        }
        value += source[i];
        i++; column++;
      }
      if (i >= source.length) {
        throw new Error(`String tidak ditutup di baris ${line}, kolom ${column}`);
      }
      i++; column++;
      tokens.push(new Token(TokenType.TEKS, value, line, column));
      continue;
    }

    if (/\d/.test(ch)) {
      let value = '';
      while (i < source.length && /\d/.test(source[i])) {
        value += source[i];
        i++; column++;
      }
      if (source[i] === '.' && /\d/.test(source[i + 1])) {
        value += '.';
        i++; column++;
        while (i < source.length && /\d/.test(source[i])) {
          value += source[i];
          i++; column++;
        }
      }
      tokens.push(new Token(TokenType.ANGKA, Number(value), line, column));
      continue;
    }

    if (/[A-Za-z_]/.test(ch)) {
      let value = '';
      while (i < source.length && /[A-Za-z0-9_]/.test(source[i])) {
        value += source[i];
        i++; column++;
      }
      const type = keywords[value] ?? TokenType.IDENTIFIER;
      tokens.push(new Token(type, value, line, column));
      continue;
    }

    if (source.startsWith('>=', i)) {
      tokens.push(new Token(TokenType.LEBIH_BESAR_SAMA, '>=', line, column));
      i += 2; column += 2; continue;
    }
    if (source.startsWith('<=', i)) {
      tokens.push(new Token(TokenType.LEBIH_KECIL_SAMA, '<=', line, column));
      i += 2; column += 2; continue;
    }
    if (source.startsWith('==', i)) {
      tokens.push(new Token(TokenType.SAMA_DENGAN, '==', line, column));
      i += 2; column += 2; continue;
    }
    if (source.startsWith('!=', i)) {
      tokens.push(new Token(TokenType.TIDAK_SAMA, '!=', line, column));
      i += 2; column += 2; continue;
    }
    if (source.startsWith('&&', i)) {
      tokens.push(new Token(TokenType.DAN, '&&', line, column));
      i += 2; column += 2; continue;
    }
    if (source.startsWith('||', i)) {
      tokens.push(new Token(TokenType.ATAU, '||', line, column));
      i += 2; column += 2; continue;
    }

    if (ch === '(') {
      tokens.push(new Token(TokenType.KURUNG_BUKA, ch, line, column));
      i++; column++; continue;
    }
    if (ch === ')') {
      tokens.push(new Token(TokenType.KURUNG_TUTUP, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '{') {
      tokens.push(new Token(TokenType.BLOK_BUKA, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '}') {
      tokens.push(new Token(TokenType.BLOK_TUTUP, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '[') {
      tokens.push(new Token(TokenType.KURUNG_BUKA, ch, line, column));
      i++; column++; continue;
    }
    if (ch === ']') {
      tokens.push(new Token(TokenType.KURUNG_TUTUP, ch, line, column));
      i++; column++; continue;
    }
    if (ch === ',') {
      tokens.push(new Token(TokenType.KOMA, ch, line, column));
      i++; column++; continue;
    }
    if (ch === ';') {
      tokens.push(new Token(TokenType.TITIK_KOMA, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '+') {
      tokens.push(new Token(TokenType.TAMBAH, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '-') {
      tokens.push(new Token(TokenType.KURANG, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '*') {
      tokens.push(new Token(TokenType.KALI, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '/') {
      tokens.push(new Token(TokenType.BAGI, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '%') {
      tokens.push(new Token(TokenType.MOD, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '>') {
      tokens.push(new Token(TokenType.LEBIH_BESAR, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '<') {
      tokens.push(new Token(TokenType.LEBIH_KECIL, ch, line, column));
      i++; column++; continue;
    }
    if (ch === '=') {
      tokens.push(new Token(TokenType.SAMA, ch, line, column));
      i++; column++; continue;
    }

    throw new Error(`Karakter tidak dikenal: '${ch}' di baris ${line}, kolom ${column}`);
  }

  tokens.push(new Token(TokenType.EOF, null, line, column));
  return tokens;
}

if (typeof module !== 'undefined') {
  module.exports = { TokenType, Token, tokenize };
}
