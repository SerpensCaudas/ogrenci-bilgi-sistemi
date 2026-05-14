import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.box import box

from database import VeritabaniYoneticisi
from services import OgrenciServisi, DersServisi

console = Console()
db  = VeritabaniYoneticisi()
os_ = OgrenciServisi(db)
ds  = DersServisi(db)
def baslik(metin: str):
    console.print(Panel(f"[bold cyan]{metin}[/]", box=box.DOUBLE_EDGE))
def hata(metin: str):
    console.print(f"[bold red]✗ {metin}[/]")
def basari(metin: str):
    console.print(f"[bold green]✓ {metin}[/]")
def sor(soru: str) -> str:
    return console.input(f"[yellow]{soru}[/] ").strip()
def ogrenci_ekle():
    baslik("Yeni Öğrenci Kaydı")
    try:
        o = os_.ogrenci_kaydet(
            sor("Öğrenci No  :"),
            sor("Ad          :"),
            sor("Soyad       :"),
            sor("Bölüm       :"),
        )
        basari(f"{o.tam_ad} kaydedildi. (ID: {o.id})")
    except Exception as e:
        hata(str(e))
def ogrenci_listele():
    baslik("Öğrenci Listesi")
    liste = db.tum_ogrenciler()
    if not liste:
        console.print("[dim]Kayıtlı öğrenci yok.[/]")
        return
    tablo = Table(box=box.SIMPLE_HEAVY, show_footer=False)
    tablo.add_column("ID",        style="dim",        width=5,  justify="right")
    tablo.add_column("Öğr. No",   style="cyan",       width=12)
    tablo.add_column("Ad Soyad",  style="bold white", width=24)
    tablo.add_column("Bölüm",     style="magenta",    width=26)
    tablo.add_column("GNO",       style="yellow",     width=6,  justify="right")
    tablo.add_column("Kredi",     style="green",      width=6,  justify="right")
    for o in liste:
        tablo.add_row(str(o.id), o.ogrenci_no, o.tam_ad,
                      o.bolum, f"{o.gno:.2f}", str(o.toplam_kredi))
    console.print(tablo)
def ders_ekle():
    baslik("Yeni Ders Ekle")
    try:
        d = ds.ders_ekle(
            sor("Ders Kodu :"),
            sor("Ders Adı  :"),
            int(sor("Kredi     :")),
        )
        basari(f"'{d.ad}' dersi eklendi. (ID: {d.id})")
    except Exception as e:
        hata(str(e))
def ders_listele():
    baslik("Ders Listesi")
    dersler = db.tum_dersler()
    if not dersler:
        console.print("[dim]Kayıtlı ders yok.[/]")
        return
    t = Table(box=box.SIMPLE_HEAVY)
    t.add_column("ID",    style="dim",    width=5, justify="right")
    t.add_column("Kod",   style="cyan",   width=10)
    t.add_column("Ders Adı", style="bold white", width=32)
    t.add_column("Kredi", style="yellow", width=6, justify="right")
    for d in dersler:
        t.add_row(str(d.id), d.kod, d.ad, str(d.kredi))
    console.print(t)
def not_gir():
    baslik("Not Girişi")
    try:
        oid = int(sor("Öğrenci ID :"))
        did = int(sor("Ders ID    :"))
        v   = float(sor("Vize       :"))
        f   = float(sor("Final      :"))
        n = os_.not_gir(oid, did, v, f)
        basari(f"Not girildi — Ortalama: {n.ortalama} [{n.harf_notu}]")
    except Exception as e:
        hata(str(e))
def not_guncelle():
    baslik("Not Güncelleme")
    try:
        oid = int(sor("Öğrenci ID :"))
        did = int(sor("Ders ID    :"))
        v   = float(sor("Yeni Vize  :"))
        f   = float(sor("Yeni Final :"))
        os_.not_guncelle(oid, did, v, f)
        basari("Not güncellendi.")
    except Exception as e:
        hata(str(e))
HARF_RENK = {
    "AA": "bright_green", "BA": "green", "BB": "cyan",
    "CB": "blue",         "CC": "yellow","DC": "yellow",
    "DD": "orange3",      "FD": "red",   "FF": "bright_red",
}
def transkript_goster():
    baslik("Öğrenci Transkripti")
    try:
        oid = int(sor("Öğrenci ID :"))
        veri = os_.transkript(oid)
        o    = veri["ogrenci"]
    except Exception as e:
        hata(str(e)); return
    gno_renk = "bright_green" if o.gno >= 2.0 else "bright_red"
    bilgi = (
        f"[bold]{o.tam_ad}[/]  |  No: [cyan]{o.ogrenci_no}[/]  |  "
        f"Bölüm: [magenta]{o.bolum}[/]  |  Kayıt: [dim]{o.kayit_tarihi}[/]\n"
        f"GNO: [{gno_renk}]{o.gno:.2f}[/]   "
        f"Geçilen Kredi: [green]{o.toplam_kredi}[/]   "
        f"Geçen: [green]{veri['gecilen_ders']}[/]   "
        f"Kalan: [red]{veri['kalan_ders']}[/]"
    )
    console.print(Panel(bilgi, title="📋 Transkript", box=box.ROUNDED))
    if not veri["notlar"]:
        console.print("[dim]  Bu öğrenciye ait not bulunmuyor.[/]"); return

    t = Table(box=box.SIMPLE_HEAVY, show_lines=True)
    t.add_column("Kod",     style="cyan",  width=10)
    t.add_column("Ders",    style="white", width=30)
    t.add_column("Kredi",   width=6,  justify="center")
    t.add_column("Vize",    width=6,  justify="right")
    t.add_column("Final",   width=6,  justify="right")
    t.add_column("Ort.",    width=7,  justify="right")
    t.add_column("Harf",    width=5,  justify="center")
    t.add_column("Durum",   width=10, justify="center")
    for n in veri["notlar"]:
        renk   = HARF_RENK.get(n.harf_notu, "white")
        durum  = "[green]GEÇTİ[/]" if n.gecti_mi else "[red]KALDI[/]"
        t.add_row(
            n.ders.kod, n.ders.ad, str(n.ders.kredi),
            f"{n.vize:.1f}", f"{n.final:.1f}",
            f"[{renk}]{n.ortalama:.1f}[/]",
            f"[{renk}]{n.harf_notu}[/]",
            durum,
        )
    console.print(t)
def demo_yukle():
    baslik("Demo Verisi Yükleniyor...")
    # Dersler
    for ders_bilgi in [
        ("MAT101","Matematik I",   4),
        ("FIZ101","Fizik I",       3),
        ("BIL101","Programlamaya Giriş", 3),
        ("TUR101","Türk Dili I",   2),
        ("ING101","İngilizce I",   3),
    ]:
        try: ds.ders_ekle(*ders_bilgi)
        except Exception: pass

    demo_ogr = [
        ("2024001","Ahmet","Yılmaz","Bilgisayar Mühendisliği"),
        ("2024002","Fatma","Kaya",  "Elektrik-Elektronik Müh."),
        ("2024003","Mehmet","Demir","Makine Mühendisliği"),
    ]
    demo_not = {
        "2024001": [(1,85,90),(2,70,75),(3,95,98),(4,80,85),(5,60,65)],
        "2024002": [(1,55,60),(2,88,92),(3,75,80),(4,70,75),(5,90,95)],
        "2024003": [(1,40,45),(2,65,70),(3,80,85),(4,75,80),(5,55,60)],
    }
    for no, ad, soyad, bolum in demo_ogr:
        try:
            o = os_.ogrenci_kaydet(no, ad, soyad, bolum)
        except Exception:
            o = db.ogrenci_no_ile_getir(no)
        if o:
            for did, v, f in demo_not.get(no, []):
                try: os_.not_gir(o.id, did, v, f)
                except Exception: pass
    basari("Demo verisi hazır. Öğrenci ID'leri 1-3.")


# ── Ana menü ───────────────────────────────────────────────────────

MENU = """
[bold cyan]═══════════════════════════════════[/]
[bold white]  ÖĞRENCİ BİLGİ SİSTEMİ[/]
[bold cyan]═══════════════════════════════════[/]
  [cyan]1[/] Öğrenci Ekle
  [cyan]2[/] Öğrenci Listesi
  [cyan]3[/] Ders Ekle
  [cyan]4[/] Ders Listesi
  [cyan]5[/] Not Gir
  [cyan]6[/] Not Güncelle
  [cyan]7[/] Transkript Görüntüle
  [cyan]8[/] Demo Verisi Yükle
  [cyan]0[/] Çıkış
[bold cyan]═══════════════════════════════════[/]
"""

EYLEMLER = {
    "1": ogrenci_ekle,
    "2": ogrenci_listele,
    "3": ders_ekle,
    "4": ders_listele,
    "5": not_gir,
    "6": not_guncelle,
    "7": transkript_goster,
    "8": demo_yukle,
}

def main():
    while True:
        console.print(MENU)
        secim = sor("Seçiminiz :").strip()
        if secim == "0":
            console.print("\n[dim]Güle güle![/]\n")
            break
        elif secim in EYLEMLER:
            console.print()
            EYLEMLER[secim]()
            console.print()
        else:
            hata("Geçersiz seçim.")


if __name__ == "__main__":
    main()
