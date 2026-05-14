import sqlite3
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
@dataclass
class Ders:
    id: Optional[int]
    kod: str
    ad: str
    kredi: int
    def __repr__(self):
        return f"Ders({self.kod} - {self.ad}, {self.kredi} kredi)"


@dataclass
class Not:
    id: Optional[int]
    ogrenci_id: int
    ders_id: int
    vize: float
    final: float
    ders: Optional[Ders] = field(default=None, repr=False)

    @property
    def ortalama(self) -> float:
        return round(self.vize * 0.4 + self.final * 0.6, 2)
    @property
    def harf_notu(self) -> str:
        o = self.ortalama
        if o >= 90: return "AA"
        elif o >= 85: return "BA"
        elif o >= 80: return "BB"
        elif o >= 75: return "CB"
        elif o >= 70: return "CC"
        elif o >= 65: return "DC"
        elif o >= 60: return "DD"
        elif o >= 50: return "FD"
        else: return "FF"
    @property
    def gecti_mi(self) -> bool:
        return self.ortalama >= 60
@dataclass
class Ogrenci:
    id: Optional[int]
    ogrenci_no: str
    ad: str
    soyad: str
    bolum: str
    kayit_tarihi: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))
    notlar: list = field(default_factory=list, repr=False)
    @property
    def tam_ad(self) -> str:
        return f"{self.ad} {self.soyad}"
    @property
    def gno(self) -> float:
        if not self.notlar:
            return 0.0
        toplam_kredi = sum(n.ders.kredi for n in self.notlar if n.ders)
        if toplam_kredi == 0:
            return 0.0
        agirlikli = sum(n.ortalama * n.ders.kredi for n in self.notlar if n.ders)
        return round(agirlikli / toplam_kredi, 2)
    @property
    def toplam_kredi(self) -> int:
        return sum(n.ders.kredi for n in self.notlar if n.ders and n.gecti_mi)
    def __repr__(self):
        return f"Ogrenci({self.ogrenci_no} - {self.tam_ad}, {self.bolum})"