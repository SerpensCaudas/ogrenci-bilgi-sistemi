
from models import Ogrenci, Ders, Not
from database import VeritabaniYoneticisi
class OgrenciServisi:
    def __init__(self, db: VeritabaniYoneticisi):
        self.db = db
    def ogrenci_kaydet(self, ogrenci_no, ad, soyad, bolum) -> Ogrenci:
        if self.db.ogrenci_no_ile_getir(ogrenci_no):
            raise ValueError(f"'{ogrenci_no}' numaralı öğrenci zaten mevcut.")
        o = Ogrenci(id=None, ogrenci_no=ogrenci_no, ad=ad, soyad=soyad, bolum=bolum)
        o.id = self.db.ogrenci_ekle(o)
        return o
    def not_gir(self, ogrenci_id: int, ders_id: int, vize: float, final: float) -> Not:
        for deger, isim in [(vize, "Vize"), (final, "Final")]:
            if not (0 <= deger <= 100):
                raise ValueError(f"{isim} notu 0–100 arasında olmalı.")
        n = Not(id=None, ogrenci_id=ogrenci_id, ders_id=ders_id, vize=vize, final=final)
        n.id = self.db.not_ekle(n)
        return n
    def not_guncelle(self, ogrenci_id: int, ders_id: int, vize: float, final: float):
        notlar = self.db.ogrenci_notlari(ogrenci_id)
        hedef = next((n for n in notlar if n.ders_id == ders_id), None)
        if not hedef:
            raise ValueError("Güncellenecek not bulunamadı.")
        hedef.vize, hedef.final = vize, final
        self.db.not_guncelle(hedef)
    def transkript(self, ogrenci_id: int) -> dict:
        o = self.db.ogrenci_getir(ogrenci_id)
        if not o:
            raise ValueError("Öğrenci bulunamadı.")
        return {
            "ogrenci": o,
            "notlar": o.notlar,
            "gno": o.gno,
            "toplam_kredi": o.toplam_kredi,
            "gecilen_ders": sum(1 for n in o.notlar if n.gecti_mi),
            "kalan_ders": sum(1 for n in o.notlar if not n.gecti_mi),
        }
class DersServisi:
    def __init__(self, db: VeritabaniYoneticisi):
        self.db = db
    def ders_ekle(self, kod, ad, kredi) -> Ders:
        d = Ders(id=None, kod=kod, ad=ad, kredi=kredi)
        d.id = self.db.ders_ekle(d)
        return d