"""
STYLE ENGINE - AI Content Style Management
3 farklı yazım stili ile varyasyonlu içerik üretimi
"""

import random
from typing import Dict, List, Optional
from datetime import datetime

# ============== STYLE DEFINITIONS ==============

STYLE_A = {
    "name": "Otoriter & Rehber",
    "code": "A",
    "purpose": "Authority ve güven oluşturmak",
    "use_cases": ["ana_domain", "rehber", "marka_analizi", "derin_icerik"],
    "system_prompt": """Sen Türkiye'nin önde gelen bahis ve bonus uzmanısın. 
Resmi, otoriter ve güven veren bir ton kullan.
E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) kriterlerine uygun yaz.

YAZIM KURALLARI:
- Resmi ve profesyonel ton
- Uzun, detaylı paragraflar (4-6 cümle)
- Teknik terimler ve açıklamaları
- Veri ve istatistik temelli anlatım
- Detaylı alt başlıklar (H2, H3)
- Kaynak ve referans belirtme tarzı
- "Araştırmalarımıza göre", "Veriler gösteriyor ki" gibi ifadeler
- Analitik ve değerlendirici yaklaşım
""",
    "intro_patterns": [
        "Kapsamlı araştırmalarımız doğrultusunda",
        "Sektör analizlerimize göre",
        "Detaylı incelememiz sonucunda",
        "Uzman değerlendirmelerimiz çerçevesinde",
        "Güncel veriler ışığında",
        "Profesyonel analizimiz kapsamında"
    ],
    "paragraph_style": "long",
    "cta_style": "subtle"
}

STYLE_B = {
    "name": "Dinamik & Kullanıcı Odaklı",
    "code": "B", 
    "purpose": "Dönüşüm ve etkileşim artırmak",
    "use_cases": ["subdomain_giris", "hizli_rehber", "landing", "popup"],
    "system_prompt": """Sen samimi ve yardımsever bir bonus danışmanısın.
Kullanıcıyla direkt konuşur gibi, sıcak ve erişilebilir bir ton kullan.
Dönüşüm odaklı ama spam olmayan içerik üret.

YAZIM KURALLARI:
- Samimi ve konuşma dili
- Kısa, etkili paragraflar (2-3 cümle)
- Soru-cevap formatı
- Doğrudan "siz" hitabı
- Emojisiz ama canlı anlatım
- Net ve doğal CTA'lar
- "Merak ediyor musunuz?", "Hemen keşfedin" gibi ifadeler
- Hızlı bilgi sunumu, bullet points
""",
    "intro_patterns": [
        "Bonus dünyasına hoş geldiniz!",
        "Doğru yerdesiniz!",
        "Size özel fırsatlar burada",
        "Hemen başlayalım",
        "Merak ettiğiniz her şey burada",
        "Kazanmaya hazır mısınız?"
    ],
    "paragraph_style": "short",
    "cta_style": "direct"
}

STYLE_C = {
    "name": "Analitik & Karşılaştırmalı",
    "code": "C",
    "purpose": "SEO derinliği ve uzun kalma süresi",
    "use_cases": ["karsilastirma", "spor_analiz", "veri_icerik", "tablo"],
    "system_prompt": """Sen veri analisti ve karşılaştırma uzmanısın.
Objektif, analitik ve veri odaklı içerik üret.
Yandex ve Bing için optimize edilmiş, derin içerik yaz.

YAZIM KURALLARI:
- Objektif ve tarafsız ton
- Tablo ve karşılaştırma formatları
- İstatistik ve yüzdelik değerler
- Artılar/eksiler listesi
- Puan ve skor sistemleri
- "X sitesi Y'den %Z daha yüksek bonus sunuyor" gibi ifadeler
- Detaylı veri analizi
- Uzun açıklama blokları
- Karşılaştırmalı değerlendirme
""",
    "intro_patterns": [
        "Detaylı karşılaştırmamızda",
        "Verilerimize göre analiz",
        "Objektif değerlendirmemiz",
        "Sayılarla bonus analizi",
        "Karşılaştırmalı inceleme",
        "Veri bazlı değerlendirme"
    ],
    "paragraph_style": "analytical",
    "cta_style": "data-driven"
}

STYLES = {
    "A": STYLE_A,
    "B": STYLE_B,
    "C": STYLE_C
}

# ============== SPAM PREVENTION ==============

SPAM_PREVENTION = {
    "banned_starts": [
        "Bu yazıda",
        "Bu makalede", 
        "Merhaba değerli okuyucular",
        "Bugün sizlerle",
        "Bu içerikte"
    ],
    "variation_rules": {
        "faq_shuffle": True,  # FAQ sıralaması karıştırılmalı
        "table_order_randomize": True,  # Tablo sırası rastgele
        "paragraph_structure_vary": True,  # Paragraf yapısı değişken
        "cta_position_vary": True  # CTA pozisyonu değişken
    },
    "min_sentence_variations": 5,  # Aynı cümle yapısı en fazla 5 kez
    "unique_intro_per_domain": True  # Her domain'de farklı giriş
}

# ============== STYLE ENGINE CLASS ==============

class StyleEngine:
    def __init__(self):
        self.styles = STYLES
        self.spam_prevention = SPAM_PREVENTION
        self.used_intros = {}  # Track used intros per domain
        self.used_patterns = {}  # Track used patterns
    
    def get_style(self, style_code: str) -> Dict:
        """Get style configuration by code"""
        return self.styles.get(style_code.upper(), STYLE_A)
    
    def select_style_for_content(
        self, 
        content_type: str, 
        domain_index: int = 0,
        section: str = "main"
    ) -> Dict:
        """
        Select appropriate style based on content type and context
        
        Args:
            content_type: Type of content (rehber, landing, karsilastirma, etc.)
            domain_index: Index of domain for rotation
            section: Section of page (intro, main, comparison, cta)
        """
        # Section-based style selection
        if section == "intro":
            return self.styles["B"]  # Always dynamic intro
        elif section == "comparison":
            return self.styles["C"]  # Always analytical for comparisons
        elif section == "deep_analysis":
            return self.styles["A"]  # Authority for deep content
        
        # Content type based selection
        content_style_map = {
            "rehber": "A",
            "landing": "B",
            "karsilastirma": "C",
            "haber": "B",
            "analiz": "C",
            "marka": "A",
            "hizli_rehber": "B",
            "spor": "C",
            "bonus_liste": "B"
        }
        
        style_code = content_style_map.get(content_type, "A")
        
        # Apply rotation for variety (every 3rd domain switches style)
        if domain_index > 0 and domain_index % 3 == 0:
            rotation = ["A", "B", "C"]
            style_code = rotation[domain_index % 3]
        
        return self.styles[style_code]
    
    def get_unique_intro(self, style: Dict, domain_id: str) -> str:
        """Get unique intro pattern for domain"""
        patterns = style["intro_patterns"].copy()
        
        # Remove already used patterns for this domain
        used = self.used_intros.get(domain_id, [])
        available = [p for p in patterns if p not in used]
        
        if not available:
            # Reset if all used
            available = patterns
            self.used_intros[domain_id] = []
        
        selected = random.choice(available)
        
        # Track usage
        if domain_id not in self.used_intros:
            self.used_intros[domain_id] = []
        self.used_intros[domain_id].append(selected)
        
        return selected
    
    def build_content_prompt(
        self,
        topic: str,
        style: Dict,
        domain_id: str,
        content_type: str = "article",
        keywords: List[str] = None,
        word_count: int = 800,
        include_faq: bool = True,
        include_table: bool = False
    ) -> str:
        """Build AI prompt with style-specific instructions"""
        
        intro = self.get_unique_intro(style, domain_id)
        
        # Base prompt
        prompt = f"""
KONU: {topic}
ANAHTAR KELİMELER: {', '.join(keywords or [])}
HEDEF KELİME SAYISI: {word_count}

YAZIM STİLİ: {style['name']}
{style['system_prompt']}

GİRİŞ TARZI: "{intro}" tarzında başla ama birebir kopyalama.

İÇERİK YAPISI:
"""
        
        # Style-specific structure
        if style["code"] == "A":
            prompt += """
1. Profesyonel giriş (2-3 paragraf)
2. Detaylı ana bölüm (H2 başlıklarla)
3. Teknik açıklamalar
4. Uzman değerlendirmesi
5. Sonuç ve öneriler
"""
        elif style["code"] == "B":
            prompt += """
1. Dikkat çekici giriş (1 paragraf)
2. Hızlı bilgi maddeleri
3. Soru-cevap bölümü
4. Pratik ipuçları
5. Aksiyon çağrısı
"""
        elif style["code"] == "C":
            prompt += """
1. Veri odaklı giriş
2. Karşılaştırma tablosu (HTML table)
3. Artılar ve eksiler listesi
4. İstatistiksel analiz
5. Veri bazlı sonuç
"""
        
        # FAQ section
        if include_faq:
            prompt += """

FAQ BÖLÜMÜ (3-5 soru):
- Soruları rastgele sırala
- Her seferde farklı sorular kullan
- Schema.org FAQ formatına uygun
"""
        
        # Table section
        if include_table:
            prompt += """

KARŞILAŞTIRMA TABLOSU:
- HTML <table> formatında
- Sıralama rastgele olmalı
- En az 5 satır veri
"""
        
        # Spam prevention rules
        prompt += f"""

SPAM ÖNLEME KURALLARI:
- Şu kalıplarla BAŞLAMA: {', '.join(self.spam_prevention['banned_starts'])}
- Her paragraf farklı yapıda olmalı
- Aynı cümle kalıbını tekrarlama
- Doğal ve özgün içerik üret
- İç link önerileri için [İÇ_LİNK: konu] kullan

HTML FORMATI: <h2>, <h3>, <p>, <ul>, <li>, <table> kullan.
"""
        
        return prompt
    
    def get_mixed_style_prompt(
        self,
        topic: str,
        domain_id: str,
        keywords: List[str] = None
    ) -> str:
        """Generate content with mixed styles for different sections"""
        
        style_b = self.styles["B"]
        style_a = self.styles["A"]
        style_c = self.styles["C"]
        
        prompt = f"""
KONU: {topic}
ANAHTAR KELİMELER: {', '.join(keywords or [])}

Bu içerik 3 FARKLI YAZIM STİLİ kullanacak:

BÖLÜM 1 - GİRİŞ ({style_b['name']}):
{style_b['system_prompt'][:200]}
- 1-2 kısa paragraf
- Dikkat çekici ve samimi

BÖLÜM 2 - DETAYLI ANALİZ ({style_a['name']}):
{style_a['system_prompt'][:200]}
- 3-4 detaylı paragraf
- H2 ve H3 başlıklar
- Profesyonel ton

BÖLÜM 3 - KARŞILAŞTIRMA ({style_c['name']}):
{style_c['system_prompt'][:200]}
- Tablo formatı
- Veri bazlı değerlendirme
- Artılar/eksiler

BÖLÜM 4 - SONUÇ ({style_b['name']}):
- Aksiyon odaklı
- Net CTA

SPAM ÖNLEME:
- Her bölüm farklı yapıda
- Tekrar eden kalıplar yok
- Doğal geçişler

HTML formatında yaz.
"""
        return prompt


# ============== STYLE TEMPLATES ==============

ARTICLE_TEMPLATES = {
    "bonus_rehber": {
        "styles": ["A", "B"],
        "sections": [
            {"name": "intro", "style": "B", "word_count": 100},
            {"name": "main", "style": "A", "word_count": 500},
            {"name": "tips", "style": "B", "word_count": 150},
            {"name": "conclusion", "style": "B", "word_count": 100}
        ]
    },
    "site_karsilastirma": {
        "styles": ["C", "B"],
        "sections": [
            {"name": "intro", "style": "B", "word_count": 100},
            {"name": "comparison", "style": "C", "word_count": 400},
            {"name": "analysis", "style": "C", "word_count": 200},
            {"name": "recommendation", "style": "B", "word_count": 100}
        ]
    },
    "spor_analiz": {
        "styles": ["C", "A"],
        "sections": [
            {"name": "intro", "style": "B", "word_count": 80},
            {"name": "stats", "style": "C", "word_count": 300},
            {"name": "analysis", "style": "A", "word_count": 300},
            {"name": "prediction", "style": "B", "word_count": 100}
        ]
    },
    "hizli_rehber": {
        "styles": ["B"],
        "sections": [
            {"name": "intro", "style": "B", "word_count": 80},
            {"name": "steps", "style": "B", "word_count": 200},
            {"name": "tips", "style": "B", "word_count": 100},
            {"name": "cta", "style": "B", "word_count": 50}
        ]
    }
}

# Singleton instance
style_engine = StyleEngine()
