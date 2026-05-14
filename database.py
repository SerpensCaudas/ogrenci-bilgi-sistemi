import sqlite3
from typing import Optional
from models import Ogrenci, Ders, Not
class VeritabaniYoneticisi:
    def __init__(self, db_yolu: str = "ogrenci_sistemi.db"):
        self.db_yolu = db_yolu
        self._baglanti: Optional[sqlite3.Connection] = None
        self._tablolari_olustur()
    def __enter__(self):
        self._baglanti = sqlite3.connect(self.db_yolu)
        self._baglanti.row_factory = sqlite3.Row
        return self._baglanti.cursor()
    def __exit__(self, exc_type, *_):
        if exc_type is None:
            self._baglanti.commit()
        else:
            self._baglanti.rollback()
        self._baglanti.close()
        self._baglanti = None
    def _tablolari_olustur(self):
        with self as cur:
            cur.executescript("""
                CREATE TABLE IF NOT EXISTS ogrenciler (
                    id           INTEGER PRIMARY KEY AUTOINCREMENT,
                    ogrenci_no   TEXT    NOT NULL UNIQUE,
                    ad           TEXT    NOT NULL,
                    soyad        TEXT    NOT NULL,
                    bolum        TEXT    NOT NULL,
                    kayit_tarihi TEXT    NOT NULL
                );

                CREATE TABLE IF NOT EXISTS dersler (
                    id    INTEGER PRIMARY KEY AUTOINCREMENT,
                    kod   TEXT    NOT NULL UNIQUE,
                    ad    TEXT    NOT NULL,
                    kredi INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS notlar (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    ogrenci_id  INTEGER NOT NULL REFERENCES ogrenciler(id) ON DELETE CASCADE,
                    ders_id     INTEGER NOT NULL REFERENCES dersler(id)    ON DELETE CASCADE,
                    vize        REAL    NOT NULL CHECK(vize  BETWEEN 0 AND 100),
                    final       REAL    NOT NULL CHECK(final BETWEEN 0 AND 100),
                    UNIQUE(ogrenci_id, ders_id)
                );
            """)
    def ogrenci_ekle(self, o: Ogrenci) -> int:
        with self as cur:
            cur.execute(
                "INSERT INTO ogrenciler (ogrenci_no,ad,soyad,bolum,kayit_tarihi) VALUES (?,?,?,?,?)",
                (o.ogrenci_no, o.ad, o.soyad, o.bolum, o.kayit_tarihi)
            )
            return cur.lastrowid
    def ogrenci_guncelle(self, o: Ogrenci):
        with self as cur:
            cur.execute(
                "UPDATE ogrenciler SET ad=?,soyad=?,bolum=? WHERE id=?",
                (o.ad, o.soyad, o.bolum, o.id)
            )
    def ogrenci_sil(self, ogrenci_id: int):
        with self as cur:
            cur.execute("DELETE FROM ogrenciler WHERE id=?", (ogrenci_id,))
    def ogrenci_getir(self, ogrenci_id: int) -> Optional[Ogrenci]:
        with self as cur:
            row = cur.execute(
                "SELECT * FROM ogrenciler WHERE id=?", (ogrenci_id,)
            ).fetchone()
        if not row:
            return None
        return self._satir_ogrenci(row)
    def ogrenci_no_ile_getir(self, ogrenci_no: str) -> Optional[Ogrenci]:
        with self as cur:
            row = cur.execute(
                "SELECT * FROM ogrenciler WHERE ogrenci_no=?", (ogrenci_no,)
            ).fetchone()
        if not row:
            return None
        return self._satir_ogrenci(row)
    def tum_ogrenciler(self) -> list[Ogrenci]:
        with self as cur:
            rows = cur.execute("SELECT * FROM ogrenciler ORDER BY soyad,ad").fetchall()
        return [self._satir_ogrenci(r) for r in rows]
    def _satir_ogrenci(self, row) -> Ogrenci:
        o = Ogrenci(
            id=row["id"], ogrenci_no=row["ogrenci_no"],
            ad=row["ad"], soyad=row["soyad"],
            bolum=row["bolum"], kayit_tarihi=row["kayit_tarihi"]
        )
        o.notlar = self.ogrenci_notlari(o.id)
        return o
    def ders_ekle(self, d: Ders) -> int:
        with self as cur:
            cur.execute(
                "INSERT INTO dersler (kod,ad,kredi) VALUES (?,?,?)",
                (d.kod, d.ad, d.kredi)
            )
            return cur.lastrowid
    def tum_dersler(self) -> list[Ders]:
        with self as cur:
            rows = cur.execute("SELECT * FROM dersler ORDER BY kod").fetchall()
        return [Ders(id=r["id"], kod=r["kod"], ad=r["ad"], kredi=r["kredi"]) for r in rows]
    def ders_getir(self, ders_id: int) -> Optional[Ders]:
        with self as cur:
            row = cur.execute("SELECT * FROM dersler WHERE id=?", (ders_id,)).fetchone()
        if not row:
            return None
        return Ders(id=row["id"], kod=row["kod"], ad=row["ad"], kredi=row["kredi"])
    def not_ekle(self, n: Not) -> int:
        with self as cur:
            cur.execute(
                "INSERT INTO notlar (ogrenci_id,ders_id,vize,final) VALUES (?,?,?,?)",
                (n.ogrenci_id, n.ders_id, n.vize, n.final)
            )
            return cur.lastrowid
    def not_guncelle(self, n: Not):
        with self as cur:
            cur.execute(
                "UPDATE notlar SET vize=?,final=? WHERE ogrenci_id=? AND ders_id=?",
                (n.vize, n.final, n.ogrenci_id, n.ders_id)
            )
    def not_sil(self, not_id: int):
        with self as cur:
            cur.execute("DELETE FROM notlar WHERE id=?", (not_id,))
    def ogrenci_notlari(self, ogrenci_id: int) -> list[Not]:
        with self as cur:
            rows = cur.execute("""
                SELECT n.*, d.kod, d.ad, d.kredi
                FROM notlar n JOIN dersler d ON n.ders_id=d.id
                WHERE n.ogrenci_id=?
                ORDER BY d.kod
            """, (ogrenci_id,)).fetchall()
        notlar = []
        for r in rows:
            d = Ders(id=r["ders_id"], kod=r["kod"], ad=r["ad"], kredi=r["kredi"])
            n = Not(id=r["id"], ogrenci_id=r["ogrenci_id"],
                    ders_id=r["ders_id"], vize=r["vize"], final=r["final"], ders=d)
            notlar.append(n)
        return notlar
    def bolum_istatistikleri(self) -> list[dict]:
        with self as cur:
            rows = cur.execute("""
                SELECT o.bolum,
                       COUNT(DISTINCT o.id) AS ogrenci_sayisi,
                       ROUND(AVG(n.vize*0.4 + n.final*0.6),2) AS ort
                FROM ogrenciler o
                LEFT JOIN notlar n ON o.id=n.ogrenci_id
                GROUP BY o.bolum
                ORDER BY o.bolum
            """).fetchall()
        return [dict(r) for r in rows]